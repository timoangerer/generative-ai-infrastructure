terraform {
  required_providers {
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

data "terraform_remote_state" "minikube" {
  backend = "local"

  config = {
    path = "./minikube/terraform.tfstate"
  }
}

provider "kubernetes" {
  host = data.terraform_remote_state.minikube.outputs.cluster_host

  client_certificate     = data.terraform_remote_state.minikube.outputs.client_certificate
  client_key             = data.terraform_remote_state.minikube.outputs.client_key
  cluster_ca_certificate = data.terraform_remote_state.minikube.outputs.cluster_ca_certificate
}

provider "helm" {
  kubernetes {
    host = data.terraform_remote_state.minikube.outputs.cluster_host

    client_certificate     = data.terraform_remote_state.minikube.outputs.client_certificate
    client_key             = data.terraform_remote_state.minikube.outputs.client_key
    cluster_ca_certificate = data.terraform_remote_state.minikube.outputs.cluster_ca_certificate
  }
}

resource "kubernetes_namespace" "genai" {
  metadata {
    name = var.kubernetes_namespace
  }
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

module "trino" {
  source     = "../../modules/trino"
  depends_on = [module.pulsar_setup]

  namespace = kubernetes_namespace.genai.metadata[0].name

  pulsar_cluster            = var.pulsar_cluster
  pulsar_service_url        = local.pulsar_service_url
  pulsar_broker_service_url = var.pulsar_broker_service_url
}

# WORKER DEPLOYMENT

resource "kubernetes_persistent_volume_claim" "models_pvc" {
  metadata {
    name      = "models-pvc"
    namespace = kubernetes_namespace.genai.metadata[0].name
  }
  spec {
    access_modes       = ["ReadWriteMany"]
    storage_class_name = "standard"
    resources {
      requests = {
        storage = "10Gi"
      }
    }
  }
}

module "download_models" {
  source      = "../../modules/models-drive"
  namespace   = kubernetes_namespace.genai.metadata[0].name
  model_links = var.model_links

  depends_on = [kubernetes_persistent_volume_claim.models_pvc]
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

variable "aws_access_key_id" {
  type      = string
  sensitive = true
}

variable "aws_secret_access_key" {
  type      = string
  sensitive = true
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
        container {
          name              = "genai-worker-sidecar"
          image             = "timoangerer/genai-worker-sidecar:latest"
          image_pull_policy = "Always"

          resources {
            limits = {
              cpu    = "500m"
              memory = "1Gi"
            }

            requests = {
              cpu    = "200m"
              memory = "0.5Gi"
            }
          }

          env_from {
            config_map_ref {
              name = "genai-worker-sidecar-config"
            }
          }

          env {
            name  = "AWS_ACCESS_KEY_ID"
            value = var.aws_access_key_id
          }

          env {
            name  = "AWS_SECRET_ACCESS_KEY"
            value = var.aws_secret_access_key
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
