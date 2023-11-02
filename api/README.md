# Generative AI API

Run the following command to start the server with open telemetry enabled:

```bash
OTEL_RESOURCE_ATTRIBUTES=service.name=gen-api OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317" OTEL_EXPORTER_OTLP_PROTOCOL=grpc opentelemetry-instrument uvicorn --app-dir=src main:app
```