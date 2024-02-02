resource "helm_release" "pulsar" {
  name       = var.pulsar_cluster
  namespace  = var.namespace
  repository = "https://pulsar.apache.org/charts"
  chart      = "pulsar"
  version    = "3.0.0"

  values = [file("${path.module}/values-simple.yaml")]

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

  set {
    name  = "pulsar_manager.service.type"
    value = "ClusterIP"
  }
}
