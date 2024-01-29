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
    path = "../../eks/terraform.tfstate"
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
    name = var.namespace
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

resource "helm_release" "metrics_server" {
  name       = "metrics-server"
  namespace  = kubernetes_namespace.genai.metadata[0].name
  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = "3.11.0"
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

  providers = {
    helm = helm
  }

  namespace = kubernetes_namespace.genai.metadata[0].name
}

module "signoz" {
  source    = "../../modules/signoz"
  namespace = kubernetes_namespace.genai.metadata[0].name
}

module "api" {
  source                      = "../../modules/api"
  namespace                   = kubernetes_namespace.genai.metadata[0].name
  otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
  pulsar_service_url          = var.pulsar_service_url
  pulsar_broker_service_url   = var.pulsar_broker_service_url
  pulsar_cluster              = var.pulsar_cluster
  pulsar_tenant               = var.pulsar_tenant
  pulsar_namespace            = var.pulsar_namespace
  trino_host                  = var.trino_host
  trino_port                  = var.trino_port
  trino_user                  = var.trino_user
  trino_catalog               = var.trino_catalog
  trino_schema                = var.trino_schema
}

module "download_models" {
  source    = "../../modules/models-drive"
  namespace = kubernetes_namespace.genai.metadata[0].name
}

module "worker" {
  source                      = "../../modules/worker"
  namespace                   = kubernetes_namespace.genai.metadata[0].name
  otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
  pulsar_service_url          = var.pulsar_service_url
  pulsar_broker_service_url   = var.pulsar_broker_service_url
  pulsar_cluster              = var.pulsar_cluster
  pulsar_tenant               = var.pulsar_tenant
  pulsar_namespace            = var.pulsar_namespace
  sd_server_url               = var.sd_server_url
  s3_bucket_name              = var.s3_bucket_name
  aws_access_key_id           = var.aws_access_key_id
  aws_secret_access_key       = var.aws_secret_access_key
}

module "trino" {
  source    = "../../modules/trino"
  namespace = kubernetes_namespace.genai.metadata[0].name
}
