resource "kubernetes_deployment" "genai_trino_deployment" {
  metadata {
    name      = "genai-trino-deployment"
    namespace = var.namespace
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "genai-trino"
      }
    }

    template {
      metadata {
        labels = {
          app = "genai-trino"
        }
      }

      spec {
        container {
          name              = "genai-trino"
          image             = "apachepulsar/pulsar-all:3.1.1"
          image_pull_policy = "IfNotPresent"
          command = ["./bin/pulsar", "sql-worker", "run",
            "-Dconnector.name=pulsar",
            "-Dpulsar.broker-service-url=http://pulsar-mini-proxy:8080",
            "-Dpulsar.web-service-url=http://pulsar-mini-proxy:8080",
            "-Dpulsar.broker-binary-service-url=pulsar://pulsar-mini-proxy:6650",
            "-Dpulsar.metadata-url=zk:pulsar-mini-zookeeper:2181",
            "-Dpulsar.bookkeeper-explicit-interval=1",  # Enables to get latest message
            "-Dpulsar.bookkeeper-use-v2-protocol=false" # Enables to get latest message
          ]

          resources {
            limits = {
              cpu    = "4000m"
              memory = "6Gi"
            }

            requests = {
              cpu    = "2000m"
              memory = "4Gi"
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "genai_trino_service" {
  metadata {
    name      = "genai-trino-service"
    namespace = var.namespace
  }

  spec {
    selector = {
      app = "genai-trino"
    }

    port {
      protocol    = "TCP"
      port        = 8081
      target_port = 8081
    }

    type = "ClusterIP"
  }
}
