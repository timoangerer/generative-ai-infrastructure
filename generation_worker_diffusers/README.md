# Generation Worker: Diffusers

## Local Development setup

Make sure to have pyenv and python 3.10.12 installed. That's the python version of the docker image image.

Make sure to activate the virtual environment.

Use pip-tools and the pip-compile command to update the requirements.txt file. Make sure to install pip tools into the virtual environment.


## Docker

### Build the image

```bash
docker build -t genai-worker-diffusers .
```

### Push the image to docker hub

```bash
docker tag genai-worker-diffusers:latest timoangerer/genai-worker-diffusers:latest
docker push timoangerer/genai-worker-diffusers:latest
```

All together:
```bash
docker build -t genai-worker-diffusers . &&
docker tag genai-worker-diffusers:latest timoangerer/genai-worker-diffusers:latest &&
docker push timoangerer/genai-worker-diffusers:latest
```

### Run the image

```bash
docker run --rm -it -v ./models:/models --env MODELS_PATH="/models" genai-worker-diffusers
```

With GPU enabled:
```bash
docker run --rm -it  -v ./models:/models --env MODELS_PATH="/models" -p 18812:18812 --gpus all genai-worker-diffusers
```

For testing purposes:
```bash
docker run --rm -it -v ./models:/models --env MODELS_PATH="/models" --gpus all genai-worker-diffusers python -m src.sample_image
```