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

```bash
docker run --rm -it -v ./models:/models --env MODELS_DIR="/models" genai-worker-diffusers
```

With GPU enabled:
```bash
docker run --rm -it  -v ./models:/models --env MODELS_DIR="/models" -p 18812:18812 --gpus all genai-worker-diffusers
```

### Localy run the image (for testing purposes)

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

4. Run the docker image for sample generation.

```bash
docker run --rm -it -v ./models:/models --env MODELS_DIR="/models" --gpus all genai-worker-diffusers python -m src.sample_image
```

Or run the the python script directly without docker

5. Download additional necessary models for diffusers.

```bash
source .venv/bin/activate
python download_hf_models.py ~/.cache/huggingface
```

6. Run the python module for sample image generation

```bash
python -m src.sample_image
```

### Localy run the RPC server

```bash
docker run --rm -it -v ./models:/models -p 18812:18812 -e MODELS_DIR=/models --gpus all genai-worker-diffusers
```