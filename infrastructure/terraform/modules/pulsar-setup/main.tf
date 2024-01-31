resource "kubernetes_config_map" "pulsar_setup_script" {
  metadata {
    name      = "pulsar-setup-script"
    namespace = var.namespace
  }

  data = {
    "setup-pulsar.sh" = <<-EOT
      #!/bin/sh

      # Define the path to pulsar-admin
      PULSAR_ADMIN="./bin/pulsar-admin"

      # Setup Pulsar Tenant
      echo "Creating Pulsar Tenant: $PULSAR_TENANT"
      $PULSAR_ADMIN --admin-url $PULSAR_URL tenants create $PULSAR_TENANT

      # Setup Pulsar Namespace
      echo "Creating Pulsar Namespace: $PULSAR_TENANT/$PULSAR_NAMESPACE"
      $PULSAR_ADMIN --admin-url $PULSAR_URL namespaces create $PULSAR_TENANT/$PULSAR_NAMESPACE

      # Setup Pulsar Topics
      IFS=','
      for topic in $PULSAR_TOPICS; do
          echo "Creating Pulsar Topic: persistent://$PULSAR_TENANT/$PULSAR_NAMESPACE/$topic"
          $PULSAR_ADMIN --admin-url $PULSAR_URL topics create persistent://$PULSAR_TENANT/$PULSAR_NAMESPACE/$topic
      done

      echo "Pulsar setup completed."
    EOT
  }
}

resource "kubernetes_job" "pulsar_setup" {
  metadata {
    name      = "pulsar-setup"
    namespace = var.namespace
  }

  timeouts {
    create = "5m"
  }

  depends_on = [kubernetes_config_map.pulsar_setup_script]

  spec {
    template {
      metadata {
        name = "pulsar-setup"
      }
      spec {
        container {
          image = "apachepulsar/pulsar-all:3.1.1"
          name  = "pulsar-setup"

          command = ["/bin/sh", "-c"]
          args    = ["cat /etc/config/setup-pulsar.sh | sh"]

          volume_mount {
            name       = "config-volume"
            mount_path = "/etc/config"
            read_only  = true
          }

          env {
            name  = "PULSAR_URL"
            value = var.pulsar_service_url
          }
          env {
            name  = "PULSAR_TENANT"
            value = var.pulsar_tenant
          }
          env {
            name  = "PULSAR_NAMESPACE"
            value = var.pulsar_namespace
          }
          env {
            name  = "PULSAR_TOPICS"
            value = join(",", var.pulsar_topics)
          }
        }

        volume {
          name = "config-volume"

          config_map {
            name = kubernetes_config_map.pulsar_setup_script.metadata[0].name
          }
        }

        restart_policy = "Never"
      }
    }

    backoff_limit = 0
  }
}
