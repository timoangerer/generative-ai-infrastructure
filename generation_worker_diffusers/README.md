# Generation Worker: Diffusers

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
docker build -t genai-worker-diffusers
```

Build, tag and push the docker image (replace `timoangerer` with your own docker hub id):
```bash
docker build -t genai-worker-diffusers . &&
docker tag genai-worker-diffusers:latest timoangerer/genai-worker-diffusers:latest &&
docker push timoangerer/genai-worker-diffusers:latest
```

### Run the image

Run the image with GPU enabled:
```bash
docker run --rm -it  -v ./models:/models --env MODELS_DIR="/models" -p 18812:18812 --gpus all genai-worker-diffusers
```

## Localy run the image

1. Build the image.

```bash
docker build -t genai-worker-diffusers .
```

2. Download a test model for image generation.

```bash
sudo wget "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors?download=true" -O ./models/v1-5-pruned-emaonly.safetensors
```

3. Create a .env file

```bash
echo "MODELS_DIR=./models" > .env
```

4. Run the docker image

```bash
docker run --rm -it  -v ./models:/models --env MODELS_DIR="/models" -p 18812:18812 --gpus all genai-worker-diffusers
```

5. Make a test request using the sample RPC client

```bash
python sample_rpc_client.py
```

6. Or optinally, run the python module for sample image generation

This stable diffusion generation functions and generates a test image.

```bash
python sample_image.py
```