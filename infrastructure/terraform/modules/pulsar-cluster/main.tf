resource "helm_release" "pulsar" {
  name       = var.pulsar_cluster
  namespace  = var.namespace
  repository = "https://pulsar.apache.org/charts"
  chart      = "pulsar"
  version    = "3.0.0"

  values = [file(var.pulsar_cluster_config_file)]

  timeout = 800

  set {
    name  = "initialize"
    value = "true"
  }

  set {
    name  = "proxy.ports.http"
    value = var.pulsar_service_port
  }

  set {
    name  = "proxy.service.type"
    value = "ClusterIP"
  }
}
