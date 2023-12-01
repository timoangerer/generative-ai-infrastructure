# Generate the requirements.txt file
FROM python:3.10.13-slim as requirements-stage

WORKDIR /tmp

RUN pip install pdm

COPY ./pyproject.toml ./pdm.lock /tmp/

RUN pdm export --without-hashes --prod -f requirements -o requirements.txt

# Pre-Download all necessary models for hf diffusers
FROM python:3.10.13-slim as hf_models_download

WORKDIR /tmp

RUN pip install huggingface_hub

COPY ./download_hf_models.py .

RUN python download_hf_models.py /hf_home


FROM nvidia/cuda:12.1.0-base-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG WORKDIR=/app

WORKDIR $WORKDIR

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY --from=hf_models_download /hf_home ./hf_home
ENV HF_HOME="./hf_home"

ARG VIRTUAL_ENV=${WORKDIR}/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src src/

CMD python3 -m src.main