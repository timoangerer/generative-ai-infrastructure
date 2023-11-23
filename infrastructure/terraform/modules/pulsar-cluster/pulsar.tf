# resource "helm_release" "pulsar-main" {
#   name       = "pulsar-main"
#   namespace  = var.namespace
#   repository = "https://pulsar.apache.org/charts"
#   chart      = "pulsar"
#   version    = "3.0.0"

#   values = [
#     "${file("../helm/pulsar-helm-chart/examples/values-minikube-simple.yaml")}"
#   ]

#   set {
#     name  = "initialize"
#     value = "true"
#   }

#   timeout = 1000
# }
