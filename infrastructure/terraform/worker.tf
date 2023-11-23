resource "kubernetes_config_map" "worker-sidecar-config" {
  metadata {
    name      = "worker-sidecar-config"
    namespace = var.namespace
  }

  data = {
    "pulsar_service_url"          = "http://localhost:8080"
    "pulsar_broker_service_url"   = "pulsar://localhost:6650/"
    "pulsar_cluster"              = "standalone"
    "pulsar_tenant"               = "public"
    "pulsar_namespace"            = "default"
    "sd_server_url"               = "http://127.0.0.1:7860"
    "s3_bucket_name"              = "sd-generations-1"
    "aws_access_key_id"           = "AKIARO5BCOA5V3MPGLVB"
    "aws_secret_access_key"       = "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"
    "otel_service_name"           = "sidecar"
    "otel_exporter_otlp_endpoint" = var.otel_exporter_otlp_endpoint
  }
}

resource "kubernetes_deployment" "genai_worker_deployment" {
  metadata {
    name      = "genai-worker"
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
              name = "worker-sidecar-config"
            }
          }
        }
      }
    }
  }
}
