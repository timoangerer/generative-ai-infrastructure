# Kubernetes
namespace             = "genai"
kubernetes_cluster_ip = "192.168.49.2"

# Pulsar
pulsar_cluster            = "pulsar-mini"
pulsar_namespace          = "genai"
pulsar_tenant             = "rocky"
pulsar_topics             = ["requested_txt2img_generation", "dlq_requested_txt2img_generation", "completed_txt2img_generation"]
pulsar_service_url        = "http://pulsar-mini-proxy:80"
pulsar_broker_service_url = "pulsar://pulsar-mini-proxy:6650/"

# TRINO
trino_host    = "http://localhost"
trino_port    = "8081"
trino_user    = "<username>"
trino_catalog = "pulsar"
trino_schema  = "public/default"

# OPEN TELEMETRY
otel_exporter_otlp_endpoint = "http://signoz-otel-collector:4317"