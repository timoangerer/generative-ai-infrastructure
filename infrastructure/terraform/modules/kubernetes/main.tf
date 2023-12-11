resource "kubernetes_namespace" "namespace" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_persistent_volume" "models" {
  metadata {
    name = "models-pv"
  }
  spec {
    storage_class_name = "standard"
    capacity = {
      storage = "20Gi"
    }
    access_modes = ["ReadWriteMany"]
    persistent_volume_source {
      host_path {
        path = "/mnt1"
      }
    }
  }
}

resource "kubernetes_persistent_volume_claim" "models" {
  metadata {
    name      = "models-pvc"
    namespace = var.namespace
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "10Gi"
      }
    }
    volume_name = kubernetes_persistent_volume.models.metadata[0].name
  }
}
