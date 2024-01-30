locals {
  model_links_content = join("\n", [for link in var.model_links : "${link.url} ${link.rename_to}"])
  model_links_hash    = md5(jsonencode(var.model_links))

  download_script = <<EOT
    #!/bin/sh

    URL_FILE="/config/models.txt"
    DEST_DIR="/models"

    mkdir -p "$DEST_DIR"
    echo "Starting download..."

    while IFS='' read -r line || [[ -n "$line" ]]; do
      echo "Processing line: $line"
      url=$(echo "$line" | awk '{print $1}')
      rename_to=$(echo "$line" | awk '{print $2}')

      filename=$(basename "$url")
      if [ ! -z "$rename_to" ]; then
        filename=$rename_to
      fi

      if [ -f "$DEST_DIR/$filename" ]; then
        echo "File $DEST_DIR/$filename already exists, skipping download."
      else
        echo "Downloading $url..."
        curl -L -o "$DEST_DIR/$filename" "$url" || echo "Failed to download $url"
      fi
    done < "$URL_FILE"

    echo "Download completed."
EOT
}

resource "kubernetes_config_map" "model_links" {
  metadata {
    name      = "model-links"
    namespace = var.namespace
  }

  data = {
    "models.txt" = local.model_links_content
  }
}

resource "kubernetes_job" "download_job" {
  metadata {
    name      = "file-download-job-${local.model_links_hash}"
    namespace = var.namespace
  }

  depends_on = [
    kubernetes_config_map.model_links
  ]

  timeouts {
    create = "5m"
  }

  spec {
    template {
      metadata {
        labels = {
          job = "file-download"
        }
      }

      spec {
        container {
          name    = "downloader"
          image   = "byrnedo/alpine-curl:latest"
          command = ["/bin/sh", "-c"]
          args    = [local.download_script]

          env {
            name  = "DOWNLOAD_DIR"
            value = "/models"
          }

          volume_mount {
            name       = "model-links-volume"
            mount_path = "/config"
          }

          volume_mount {
            name       = "storage"
            mount_path = "/models"
          }
        }

        volume {
          name = "model-links-volume"

          config_map {
            name = kubernetes_config_map.model_links.metadata[0].name
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
