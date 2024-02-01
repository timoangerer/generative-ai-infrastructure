resource "helm_release" "signoz" {
  name       = "signoz"
  namespace  = var.namespace
  repository = "https://charts.signoz.io"
  chart      = "signoz"
  version    = "0.30.2"

  timeout = 1000
}
