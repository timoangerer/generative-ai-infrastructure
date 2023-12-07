namespace                   = "genai"
otel_exporter_otlp_endpoint = "http://signoz-otel-collector:4317"
pulsar_cluster              = "pulsar-mini"
pulsar_namespace            = "genai"
pulsar_tenant               = "rocky"
pulsar_topics               = ["requested_txt2img_generation", "dlq_requested_txt2img_generation", "completed_txt2img_generation"]
