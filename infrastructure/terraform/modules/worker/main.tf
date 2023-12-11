resource "kubernetes_config_map" "genai-worker-sidecar-config" {
  metadata {
    name      = "genai-worker-sidecar-config"
    namespace = var.namespace
  }

  data = {
    pulsar_service_url            = var.pulsar_service_url
    pulsar_broker_service_url     = var.pulsar_broker_service_url
    pulsar_cluster                = var.pulsar_cluster
    pulsar_tenant                 = var.pulsar_tenant
    pulsar_namespace              = var.pulsar_namespace
    sd_server_url                 = var.sd_server_url
    s3_bucket_name                = var.s3_bucket_name
    AWS_ACCESS_KEY_ID             = var.aws_access_key_id
    AWS_SECRET_ACCESS_KEY         = var.aws_secret_access_key
    "otel_service_name"           = "sidecar"
    "otel_exporter_otlp_endpoint" = var.otel_exporter_otlp_endpoint
  }
}

resource "kubernetes_config_map" "genai-worker-diffusers-config" {
  metadata {
    name      = "genai-worker-diffusers-config"
    namespace = var.namespace
  }

  data = {
    models_path = "/models"
  }
}

resource "kubernetes_deployment" "genai_worker_deployment" {
  metadata {
    name      = "genai-worker-deployment"
    namespace = var.namespace
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "genai-worker"
      }
    }

    template {
      metadata {
        labels = {
          app = "genai-worker"
        }
      }

      spec {
        container {
          name              = "genai-worker-sidecar"
          image             = "timoangerer/genai-worker-sidecar:latest"
          image_pull_policy = "Always"

          resources {
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }

            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
          }

          env_from {
            config_map_ref {
              name = "genai-worker-sidecar-config"
            }
          }
        }
        container {
          name              = "genai-worker-diffusers"
          image             = "timoangerer/genai-worker-diffusers:latest"
          image_pull_policy = "Always"

          resources {
            limits = {
              "nvidia.com/gpu" = 1
              # cpu    = "1000m"
              # memory = "3000Mi"
            }

            requests = {
              "nvidia.com/gpu" = 1
              # cpu    = "500m"
              # memory = "512Mi"
            }
          }
          # env {
          #   name  = "SAMPLE_MODE"
          #   value = "true"
          # }

          env_from {
            config_map_ref {
              name = "genai-worker-diffusers-config"
            }
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
      }
    }
  }
}
