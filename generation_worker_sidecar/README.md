# Generation Worker Sidecar

## Docker

Build the image:

```bash
docker build -t genai-worker-sidecar .
```

Push the image to docker hub:

```bash
docker tag genai-worker-sidecar:latest timoangerer/genai-worker-sidecar:latest
docker push timoangerer/genai-worker-sidecar:latest
```