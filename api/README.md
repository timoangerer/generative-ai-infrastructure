# Generative AI API

## Run locally

1. Install the depdencies and activate the python venv:
```bash
pdm install
```

2. Create a `.env` file in the root directory and add all necessary values found in the `src/config.py` file.

3. Run the application
```bash
pdm start
```

Run the following command to start the server with open telemetry enabled:
```bash
OTEL_RESOURCE_ATTRIBUTES=service.name=gen-api OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317" OTEL_EXPORTER_OTLP_PROTOCOL=grpc opentelemetry-instrument uvicorn --app-dir=src main:app
```

## Docker

Build the docker image
```bash
docker build -t genai-api
```

Run the docker image
```bash
docker run --rm -it --env-file .env -p 8000:8000 genai-api:latest
```

Build, tag and push the docker image (replace `timoangerer` with your own docker hub id):
```bash
docker build -t genai-api . &&
docker tag genai-api:latest timoangerer/genai-api:latest &&
docker push timoangerer/genai-api:latest
```