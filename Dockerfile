ARG PYTHON_IMAGE_VERSION=3.11

FROM python:${PYTHON_IMAGE_VERSION}-slim-bookworm AS base

LABEL maintainer="ToshY (github.com/ToshY)"

ENV PIP_ROOT_USER_ACTION ignore

WORKDIR /build

RUN apt-get update \
    && apt install -y wget \
    && wget -O /usr/share/keyrings/gpg-pub-moritzbunkus.gpg https://mkvtoolnix.download/gpg-pub-moritzbunkus.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/gpg-pub-moritzbunkus.gpg] https://mkvtoolnix.download/debian/ bookworm main" > /etc/apt/sources.list.d/mkvtoolnix.download.list \
    && echo "deb-src [signed-by=/usr/share/keyrings/gpg-pub-moritzbunkus.gpg] https://mkvtoolnix.download/debian/ bookworm main" >> /etc/apt/sources.list.d/mkvtoolnix.download.list \
    && apt-get update \
    && apt install -y mkvtoolnix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

FROM base AS prod

COPY . .

RUN pip install .

WORKDIR /app

RUN set -ex \
    && /bin/bash -c 'mkdir -p ./{input,output,preset}' \
    && cp -r /build/preset ./ \
    && rm -rf /build

ENTRYPOINT ["mkvresort"]

FROM base AS dev

WORKDIR /app

COPY requirements.dev.txt ./

RUN pip install --no-cache-dir -r requirements.dev.txt