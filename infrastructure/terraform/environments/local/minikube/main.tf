provider "minikube" {
  kubernetes_version = "v1.28.3"
}

resource "minikube_cluster" "minikube_cluster" {
  driver            = "docker"
  container_runtime = "docker"

  cluster_name = "minikube"
  addons = [
    "default-storageclass",
    "storage-provisioner",
  ]
  cpus   = 3
  memory = "12gb"
  gpus   = "nvidia"
}
