resource "kubernetes_config_map" "api-config" {
  metadata {
    name      = "api-config"
    namespace = var.namespace
  }

  data = {
    "pulsar_service_url"          = "http://localhost:8080"
    "pulsar_broker_service_url"   = "pulsar://localhost:6650/"
    "pulsar_cluster"              = "standalone"
    "pulsar_tenant"               = "public"
    "pulsar_namespace"            = "default"
    "trino_host"                  = "http://localhost"
    "trino_port"                  = "8081"
    "trino_user"                  = "<username>"
    "trino_catalog"               = "pulsar"
    "trino_schema"                = "public/default"
    "otel_service_name"           = "genai-api"
    "otel_exporter_otlp_endpoint" = var.otel_exporter_otlp_endpoint
  }
}


resource "kubernetes_deployment" "genai_api_deployment" {
  metadata {
    name      = "genai-api-deployment"
    namespace = var.namespace
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "genai-api"
      }
    }

    template {
      metadata {
        labels = {
          app = "genai-api"
        }
      }

      spec {
        container {
          name              = "genai-api"
          image             = "timoangerer/genai-api:latest"
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

          port {
            container_port = 8000
          }

          env_from {
            config_map_ref {
              name = "api-config"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "genai_api_service" {
  metadata {
    name      = "genai-api-service"
    namespace = var.namespace
  }

  spec {
    selector = {
      app = "genai-api"
    }

    port {
      protocol    = "TCP"
      port        = 8000
      target_port = 8000
    }

    type = "ClusterIP"
  }
}

