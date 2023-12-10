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
    aws_access_key_id             = var.aws_access_key_id
    aws_secret_access_key         = var.aws_secret_access_key
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
              name = "genai-worker-sidecar-config"
            }
          }
        }
      }
    }
  }
}
