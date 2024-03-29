terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.48.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.23.0"
    }

    helm = {
      source  = "hashicorp/helm"
      version = "2.11.0"
    }
  }
}

data "terraform_remote_state" "eks" {
  backend = "local"

  config = {
    path = "./eks/terraform.tfstate"
  }
}

# Retrieve EKS cluster information
provider "aws" {
  region = data.terraform_remote_state.eks.outputs.region
}

data "aws_eks_cluster" "cluster" {
  name = data.terraform_remote_state.eks.outputs.cluster_name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      data.aws_eks_cluster.cluster.name
    ]
  }
}

resource "kubernetes_namespace" "genai" {
  metadata {
    name = var.kubernetes_namespace
  }
}

resource "kubernetes_service_account" "s3_interaction_sa" {
  metadata {
    name      = "s3-interaction"
    namespace = kubernetes_namespace.genai.metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = data.terraform_remote_state.eks.outputs.iam_s3_interaction_role_arn
    }
  }
}

resource "kubernetes_storage_class" "efs" {
  metadata {
    name = "efs-sc"

  }
  storage_provisioner = "efs.csi.aws.com"
  parameters = {
    provisioningMode = "efs-ap"
    fileSystemId     = data.terraform_remote_state.eks.outputs.models_efs_id
    directoryPerms   = "777"
  }
}
resource "kubernetes_persistent_volume" "models_pv" {
  metadata {
    name = "models-pv"
  }
  spec {
    capacity = {
      storage = "20Gi"
    }
    access_modes       = ["ReadWriteMany"]
    storage_class_name = kubernetes_storage_class.efs.metadata[0].name
    persistent_volume_source {
      csi {
        driver        = "efs.csi.aws.com"
        volume_handle = data.terraform_remote_state.eks.outputs.models_efs_id
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "models_pvc" {
  metadata {
    name      = "models-pvc"
    namespace = kubernetes_namespace.genai.metadata[0].name
  }
  spec {
    access_modes       = ["ReadWriteMany"]
    storage_class_name = kubernetes_storage_class.efs.metadata[0].name
    resources {
      requests = {
        storage = "10Gi"
      }
    }
    volume_name = kubernetes_persistent_volume.models_pv.id
  }
}

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = [
        "eks",
        "get-token",
        "--cluster-name",
        data.aws_eks_cluster.cluster.name
      ]
    }
  }
}

resource "helm_release" "nvidia_k8s_device_plugin" {
  name       = "nvidia-k8s-device-plugin"
  namespace  = kubernetes_namespace.genai.metadata[0].name
  repository = "https://nvidia.github.io/k8s-device-plugin"
  chart      = "nvidia-device-plugin "
  version    = "0.14.3"
}

module "pulsar_cluster" {
  source = "../../modules/pulsar-cluster"

  namespace                  = kubernetes_namespace.genai.metadata[0].name
  pulsar_cluster             = var.pulsar_cluster
  pulsar_service_port        = var.pulsar_service_port
  pulsar_cluster_config_file = var.pulsar_cluster_config_file
}

module "pulsar_setup" {
  source     = "../../modules/pulsar-setup"
  depends_on = [module.pulsar_cluster]

  namespace = kubernetes_namespace.genai.metadata[0].name

  pulsar_service_url = local.pulsar_service_url
  pulsar_namespace   = var.pulsar_namespace
  pulsar_tenant      = var.pulsar_tenant
  pulsar_topics      = var.pulsar_topics
}

module "signoz" {
  source    = "../../modules/signoz"
  namespace = kubernetes_namespace.genai.metadata[0].name
}

module "api" {
  source     = "../../modules/api"
  depends_on = [module.pulsar_setup]

  namespace                   = kubernetes_namespace.genai.metadata[0].name
  otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint

  pulsar_service_url        = local.pulsar_service_url
  pulsar_broker_service_url = var.pulsar_broker_service_url
  pulsar_cluster            = var.pulsar_cluster
  pulsar_tenant             = var.pulsar_tenant
  pulsar_namespace          = var.pulsar_namespace

  trino_host    = var.trino_host
  trino_port    = var.trino_port
  trino_user    = var.trino_user
  trino_catalog = var.trino_catalog
  trino_schema  = var.trino_schema
}

module "download_models" {
  source      = "../../modules/models-drive"
  namespace   = kubernetes_namespace.genai.metadata[0].name
  model_links = var.model_links
}

# module "worker" {
#   source     = "../../modules/worker"
#   depends_on = [module.pulsar_setup]

#   namespace            = kubernetes_namespace.genai.metadata[0].name
#   service_account_name = kubernetes_service_account.s3_interaction_sa.metadata[0].name
#   models_pvc           = kubernetes_persistent_volume_claim.models_pvc.metadata[0].name

#   otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
#   pulsar_service_url          = local.pulsar_service_url
#   pulsar_broker_service_url   = var.pulsar_broker_service_url
#   pulsar_cluster              = var.pulsar_cluster
#   pulsar_tenant               = var.pulsar_tenant
#   pulsar_namespace            = var.pulsar_namespace
#   sd_server_url               = local.sd_server_url
#   s3_bucket_name              = var.s3_bucket_name
# }

module "trino" {
  source     = "../../modules/trino"
  depends_on = [module.pulsar_setup]

  namespace = kubernetes_namespace.genai.metadata[0].name

  pulsar_cluster            = var.pulsar_cluster
  pulsar_service_url        = local.pulsar_service_url
  pulsar_broker_service_url = var.pulsar_broker_service_url
}

resource "kubernetes_config_map" "genai-worker-sidecar-config" {
  metadata {
    name      = "genai-worker-sidecar-config"
    namespace = kubernetes_namespace.genai.metadata[0].name
  }

  data = {
    pulsar_service_url          = local.pulsar_service_url
    pulsar_broker_service_url   = var.pulsar_broker_service_url
    pulsar_cluster              = var.pulsar_cluster
    pulsar_tenant               = var.pulsar_tenant
    pulsar_namespace            = var.pulsar_namespace
    sd_server_url               = local.sd_server_url
    s3_bucket_name              = var.s3_bucket_name
    otel_service_name           = "sidecar"
    otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
  }
}

resource "kubernetes_config_map" "genai-worker-diffusers-config" {
  metadata {
    name      = "genai-worker-diffusers-config"
    namespace = kubernetes_namespace.genai.metadata[0].name
  }

  data = {
    models_path = "/models"
  }
}

resource "kubernetes_deployment" "genai_worker_deployment" {
  metadata {
    name      = "genai-worker-deployment"
    namespace = kubernetes_namespace.genai.metadata[0].name
  }

  spec {
    replicas = 1

    strategy {
      type = "Recreate"
    }

    selector {
      match_labels = {
        app = "genai-worker"
      }
    }

    template {
      metadata {
        labels = {
          app = "genai-worker"
        }
      }

      spec {
        node_selector = {
          "workload-type" = "gpu"
        }

        service_account_name = kubernetes_service_account.s3_interaction_sa.metadata[0].name

        container {
          name              = "genai-worker-sidecar"
          image             = "timoangerer/genai-worker-sidecar:latest"
          image_pull_policy = "Always"

          resources {
            limits = {
              cpu    = "1000m"
              memory = "1Gi"
            }

            requests = {
              cpu    = "500m"
              memory = "0.5Gi"
            }
          }

          env_from {
            config_map_ref {
              name = "genai-worker-sidecar-config"
            }
          }
        }
        container {
          name              = "genai-worker-diffusers"
          image             = "timoangerer/genai-worker-diffusers:latest"
          image_pull_policy = "Always"

          resources {
            limits = {
              "nvidia.com/gpu" = 1
            }

            requests = {
              "nvidia.com/gpu" = 1
            }
          }

          env {
            name  = "MODELS_DIR"
            value = "/models"
          }

          env_from {
            config_map_ref {
              name = "genai-worker-diffusers-config"
            }
          }

          volume_mount {
            name       = "storage"
            mount_path = "/models"
          }
        }
        volume {
          name = "storage"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.models_pvc.metadata[0].name
            read_only  = true
          }
        }
      }
    }
  }
}
