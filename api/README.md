# Generative AI API

## Docker

Build the docker image:

```bash
docker build -t genai-api .
```

Push Docker image to Docker Hub:

```bash
docker tag genai-api:latest timoangerer/genai-api:latest
docker push timoangerer/genai-api:latest
```

Run the following command to start the server with open telemetry enabled:

```bash
OTEL_RESOURCE_ATTRIBUTES=service.name=gen-api OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317" OTEL_EXPORTER_OTLP_PROTOCOL=grpc opentelemetry-instrument uvicorn --app-dir=src main:app
```