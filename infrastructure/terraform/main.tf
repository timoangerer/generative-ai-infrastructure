module "kubernetes" {
  source    = "./modules/kubernetes"
  namespace = var.namespace
}

module "pulsar_cluster" {
  source    = "./modules/pulsar-cluster"
  namespace = var.namespace
}

module "pulsar_setup" {
  source           = "./modules/pulsar-setup"
  pulsar_cluster   = var.pulsar_cluster
  pulsar_namespace = var.pulsar_namespace
  pulsar_tenant    = var.pulsar_tenant
  pulsar_topics    = var.pulsar_topics
}

module "signoz" {
  source    = "./modules/signoz"
  namespace = var.namespace
}
