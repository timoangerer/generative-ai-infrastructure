variable "pulsar_cluster" {
  description = "Name of the pulsar cluster"
  type        = string
  default     = "pulsar-mini"
}

resource "helm_release" "pulsar" {
  name       = var.pulsar_cluster
  namespace  = var.namespace
  repository = "https://pulsar.apache.org/charts"
  chart      = "pulsar"
  version    = "3.0.0"
  timeout    = 800

  values = [file("${path.module}/values-minikube-simple.yaml")]

  set {
    name  = "initialize"
    value = "true"
  }

  set {
    name  = "proxy.service.type"
    value = "NodePort"
  }

  set {
    name  = "proxy.ports.http"
    value = "8080"
  }

  set {
    name  = "pulsar_manager.service.type"
    value = "NodePort"
  }
}
