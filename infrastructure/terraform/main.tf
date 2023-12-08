terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.23.0"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "kubernetes" {
  source    = "./modules/kubernetes"
  namespace = var.namespace
}

module "pulsar_cluster" {
  source    = "./modules/pulsar-cluster"
  namespace = var.namespace
}

data "kubernetes_service" "pulsar_proxy" {
  depends_on = [module.pulsar_cluster]
  metadata {
    name      = "pulsar-mini-proxy"
    namespace = var.namespace
  }
}

module "pulsar_setup" {
  source           = "./modules/pulsar-setup"
  namespace        = var.namespace
  pulsar_cluster   = var.pulsar_cluster
  pulsar_namespace = var.pulsar_namespace
  pulsar_tenant    = var.pulsar_tenant
  pulsar_topics    = var.pulsar_topics
  pulsar_proxy_url = "http://${var.kubernetes_cluster_ip}:${data.kubernetes_service.pulsar_proxy.spec[0].port[0].node_port}"
}

module "signoz" {
  source    = "./modules/signoz"
  namespace = var.namespace
}

module "api" {
  source                      = "./modules/api"
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
