# Models Drive

## Docker

### Run image locally

    docker run --rm -it -v ./models:/models -e URL_FILE_PATH=models.txt -e DOWNLOAD_DIR=/models models-drive

### Build image

    docker build -t models-drive .

### Push Docker image to Docker Hub:

```bash
docker build -t models-drive . &&
docker tag models-drive:latest timoangerer/models-drive:latest &&
docker push timoangerer/models-drive:latest
```