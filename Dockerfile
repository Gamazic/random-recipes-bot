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


FROM python:3.9.7-slim-bullseye

COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

WORKDIR /app
COPY . .
VOLUME ["./logs"]