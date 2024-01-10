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

    pulsar = {
      source  = "streamnative/pulsar"
      version = "0.2.0"
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

resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
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

module "pulsar_cluster" {
  source = "../../modules/pulsar-cluster"

  providers = {
    helm = helm
  }

  namespace = var.namespace
}

# resource "null_resource" "port_forward_pulsar_proxy" {
#   provisioner "local-exec" {
#     command = <<EOT
#       kubectl port-forward services/pulsar-mini-proxy 8080:8080 6650:6650 -n genai
#     EOT
#   }
# }

provider "pulsar" {
  web_service_url = "http://127.0.0.1:8080"
}

module "pulsar_setup" {
  source           = "../../modules/pulsar-setup"
  namespace        = var.namespace
  pulsar_cluster   = var.pulsar_cluster
  pulsar_namespace = var.pulsar_namespace
  pulsar_tenant    = var.pulsar_tenant
  pulsar_topics    = var.pulsar_topics
}

# # module "signoz" {
# #   source    = "./modules/signoz"
# #   namespace = var.namespace
# # }

module "api" {
  source                      = "../../modules/api"
  namespace                   = var.namespace
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

# module "worker" {
#   source                      = "./modules/worker"
#   namespace                   = var.namespace
#   otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
#   pulsar_service_url          = var.pulsar_service_url
#   pulsar_broker_service_url   = var.pulsar_broker_service_url
#   pulsar_cluster              = var.pulsar_cluster
#   pulsar_tenant               = var.pulsar_tenant
#   pulsar_namespace            = var.pulsar_namespace
#   sd_server_url               = var.sd_server_url
#   s3_bucket_name              = var.s3_bucket_name
#   aws_access_key_id           = var.aws_access_key_id
#   aws_secret_access_key       = var.aws_secret_access_key
# }

# module "trino" {
#   source    = "./modules/trino"
#   namespace = var.namespace
# }
