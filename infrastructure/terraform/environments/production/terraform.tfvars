# KUBERNETES
kubernetes_namespace = "genai"

# PULSAR
pulsar_cluster            = "pulsar"
pulsar_namespace          = "genai"
pulsar_tenant             = "rocky"
pulsar_topics             = ["requested_txt2img_generation", "dlq_requested_txt2img_generation", "completed_txt2img_generation"]
pulsar_service_host       = "http://pulsar-proxy"
pulsar_service_port       = "8080"
pulsar_broker_service_url = "pulsar://pulsar-proxy:6650/"

# TRINO
trino_host    = "http://genai-trino-service"
trino_port    = "8081"
trino_user    = "<username>"
trino_catalog = "pulsar"
trino_schema  = "rocky/genai"

# OPEN TELEMETRY
otel_exporter_otlp_endpoint = "http://signoz-otel-collector:4317"

# WORKER
sd_server_host = "http://127.0.0.1"
sd_server_port = "18812"
s3_bucket_name = "genai-generated-images-1"

# MODELS
model_links = [
  {
    url       = "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors?download=true"
    rename_to = "v1-5-pruned-emaonly.safetensors"
  },
  {
    url       = "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_6.31_BakedVae_pruned.safetensors?download=true"
    rename_to = "DreamShaper_6.safetensors"
  }
]
