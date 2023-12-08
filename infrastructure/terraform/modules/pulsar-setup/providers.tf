terraform {
  required_providers {
    pulsar = {
      source  = "streamnative/pulsar"
      version = "0.2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.23.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

data "kubernetes_service" "pulsar_proxy" {
  metadata {
    name      = "pulsar-mini-proxy"
    namespace = var.namespace
  }
}

provider "pulsar" {
  web_service_url = var.pulsar_proxy_url
}
