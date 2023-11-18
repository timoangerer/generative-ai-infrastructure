FROM python:3.10.13-slim as requirements-stage

WORKDIR /tmp

RUN pip install pdm

COPY ./pyproject.toml ./pdm.lock /tmp/

RUN pdm export --without-hashes --prod -f requirements -o requirements.txt

FROM python:3.10.13-slim

WORKDIR /usr/app/

ENV VIRTUAL_ENV=/usr/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=requirements-stage /tmp/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src .

ENV APP_PORT=8000
EXPOSE $APP_PORT

CMD python -m uvicorn main:app --host 0.0.0.0 --port $APP_PORT