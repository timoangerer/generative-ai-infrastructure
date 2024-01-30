resource "kubernetes_job" "download_job" {
  metadata {
    name      = "file-download-job"
    namespace = var.namespace
  }

  spec {
    template {
      metadata {
        labels = {
          job = "file-download"
        }
        annotations = {
          "kubectl.kubernetes.io/restartedAt" = timestamp()
        }
      }

      spec {
        container {
          name              = "downloader"
          image             = "timoangerer/models-drive:latest"
          image_pull_policy = "Always"

          env {
            name  = "URL_FILE_PATH"
            value = "models.txt"
          }

          env {
            name  = "DOWNLOAD_DIR"
            value = "/models"
          }

          volume_mount {
            name       = "storage"
            mount_path = "/models"
          }
        }

        volume {
          name = "storage"

          persistent_volume_claim {
            claim_name = "models-pvc"
          }
        }

        restart_policy = "Never"
      }
    }

    backoff_limit = 0
  }
}
