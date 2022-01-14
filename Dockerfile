FROM python:3.9

WORKDIR /home

# Install Poetry
RUN set +x \
 && apt update \
 && apt install -y curl \
 && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python \
 && cd /usr/local/bin \
 && ln -s /opt/poetry/bin/poetry \
 && poetry config virtualenvs.create false \
 && rm -rf /var/lib/apt/lists/*

# copy code & install dependencies
COPY . /home/
RUN poetry install -n --no-dev
VOLUME ["/home/logs"]

ENTRYPOINT ["python", "server.py"]