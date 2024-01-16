resource "kubernetes_config_map" "genai-api-config" {
  metadata {
    name      = "genai-api-config"
    namespace = var.namespace
  }

  data = {
    pulsar_service_url          = var.pulsar_service_url
    pulsar_broker_service_url   = var.pulsar_broker_service_url
    pulsar_cluster              = var.pulsar_cluster
    pulsar_tenant               = var.pulsar_tenant
    pulsar_namespace            = var.pulsar_namespace
    trino_host                  = var.trino_host
    trino_port                  = var.trino_port
    trino_user                  = var.trino_user
    trino_catalog               = var.trino_catalog
    trino_schema                = var.trino_schema
    otel_service_name           = "genai-api"
    otel_exporter_otlp_endpoint = var.otel_exporter_otlp_endpoint
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
              cpu    = "2000m"
              memory = "1.5Gi"
            }

            requests = {
              cpu    = "1000m"
              memory = "1Gi"
            }
          }

          port {
            container_port = 8000
          }

          env_from {
            config_map_ref {
              name = "genai-api-config"
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

