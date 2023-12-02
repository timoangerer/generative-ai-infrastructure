# Generation Worker: Diffusers

## Local Development setup

Make sure to have pyenv and python 3.10.12 installed. That's the python version of the docker image image.

Make sure to activate the virtual environment.

Use pip-tools and the pip-compile command to update the requirements.txt file. Make sure to install pip tools into the virtual environment.


## Docker

### Build the image

```bash
docker build -t generation-worker .
```

### Run the image

```bash
docker run --rm -v ./models:/models --env MODELS_PATH="/models" generation-worker
```

With GPU enabled:
```bash
docker run --rm -v ./models:/models --env MODELS_PATH="/models" --gpus all generation-worker
```

For testing purposes:
```bash
docker run --rm -v ./models:/models -v ./hf_cache:/hf_cache --env MODELS_PATH="/models" --env HF_HOME="/hf_cache" generation-worker python -m src.sample_image
```