FROM python:3.9.7-slim-bullseye as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \ 
        curl \
        gcc \
        && apt-get autoremove -yqq --purge \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"

COPY ./poetry.lock ./pyproject.toml ./

RUN poetry export --output requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# SSL
ARG WEBHOOK_HOST=""
RUN openssl genrsa -out webhook_pkey.pem 2048 &&\
        openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem -subj "/CN=${WEBHOOK_HOST}"


FROM python:3.9.7-slim-bullseye

# python dependencies
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# ssl cert
COPY --from=builder /app/webhook_cert.pem /app/webhook_pkey.pem /app/

WORKDIR /app
COPY . .
VOLUME ["./logs"]