output "cluster_host" {
  value = minikube_cluster.minikube_cluster.host
}

output "client_certificate" {
  value     = minikube_cluster.minikube_cluster.client_certificate
  sensitive = true
}

output "client_key" {
  value     = minikube_cluster.minikube_cluster.client_key
  sensitive = true
}

output "cluster_ca_certificate" {
  value     = minikube_cluster.minikube_cluster.cluster_ca_certificate
  sensitive = true
}
