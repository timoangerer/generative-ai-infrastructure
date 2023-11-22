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
    pulsar = {
      source  = "streamnative/pulsar"
      version = "0.2.0"
    }
  }
}

variable "namespace" {
  description = "The primary namespace the entire infrastructure"
  type        = string
  default     = "genai1"
}


provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
  }
}

provider "helm" {
  kubernetes {
    config_path = "~/.kube/config"
  }
}

resource "helm_release" "pulsar-main" {
  name       = "pulsar-main"
  namespace  = var.namespace
  repository = "https://pulsar.apache.org/charts"
  chart      = "pulsar"
  version    = "3.0.0"

  values = [
    "${file("../helm/pulsar-helm-chart/examples/values-minikube-simple.yaml")}"
  ]

  set {
    name  = "initialize"
    value = "true"
  }

  timeout = 1000
}


# provider "pulsar" {
#   web_service_url = "http://127.0.0.1:51195"
# }

# resource "pulsar_tenant" "tenant" {
#   tenant           = "rocky"
#   allowed_clusters = ["pulsar-mini"]
# }

# resource "pulsar_namespace" "gen" {
#   tenant    = pulsar_tenant.tenant.tenant
#   namespace = "gen"
# }

# variable "topics" {
#   description = "List of topic names"
#   type        = list(string)
#   default     = ["requested_txt2img_generation", "dlq_requested_txt2img_generation", "completed_txt2img_generation"]
# }

# resource "pulsar_topic" "topics" {
#   for_each   = toset(var.topics)
#   topic_name = each.value
#   tenant     = pulsar_tenant.tenant.tenant
#   namespace  = pulsar_namespace.gen.namespace
#   partitions = 0
#   topic_type = "persistent"
# }

# provider "helm" {
#   kubernetes {
#     config_path = "~/.kube/config"
#   }
# }


