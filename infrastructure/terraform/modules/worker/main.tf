resource "kubernetes_config_map" "genai-worker-sidecar-config" {
  metadata {
    name      = "genai-worker-sidecar-config"
    namespace = var.namespace
  }

  data = {
    pulsar_service_url          = var.pulsar_service_url
    pulsar_broker_service_url   = var.pulsar_broker_service_url
    pulsar_cluster              = var.pulsar_cluster
    pulsar_tenant               = var.pulsar_tenant
    pulsar_namespace            = var.pulsar_namespace
    sd_server_url               = var.sd_server_url
    s3_bucket_name              = var.s3_bucket_name
    otel_service_name           = "sidecar"
    otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
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

    strategy {
      type = "Recreate"
    }

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
        node_selector = {
          "workload-type" = "gpu"
        }

        service_account_name = "s3-interaction"

        container {
          name              = "genai-worker-sidecar"
          image             = "timoangerer/genai-worker-sidecar:latest"
          image_pull_policy = "Always"

          resources {
            limits = {
              cpu    = "1000m"
              memory = "1Gi"
            }

            requests = {
              cpu    = "500m"
              memory = "0.5Gi"
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
            }

            requests = {
              "nvidia.com/gpu" = 1
            }
          }

          env {
            name  = "MODELS_DIR"
            value = "/models"
          }

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
            read_only  = true
          }
        }
      }
    }
  }
}
