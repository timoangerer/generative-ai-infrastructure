# Generation Worker Sidecar

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

## Docker

Build the docker image:
```bash
docker build -t genai-worker-sidecar
```

Build, tag and push the docker image (replace `timoangerer` with your own docker hub id):
```bash
docker build -t genai-worker-sidecar . &&
docker tag genai-worker-sidecar:latest timoangerer/genai-worker-sidecar:latest &&
docker push timoangerer/genai-worker-sidecar:latest
```

Run the docker image
```bash
docker run --rm -it genai-worker-sidecar
```