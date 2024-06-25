<h1 align="center"> 📺 MKVresort </h1>

<div align="center">
    <img src="https://img.shields.io/github/v/release/toshy/mkvresort?label=Release&sort=semver" alt="Current bundle version" />
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/codestyle.yml?branch=main&label=Black" alt="Black">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/codequality.yml?branch=main&label=Ruff" alt="Ruff">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/statictyping.yml?branch=main&label=Mypy" alt="Mypy">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/security.yml?branch=main&label=Security%20check" alt="Security check" />
</div>

## 📝 Quickstart

A command-line utility for resorting streams.

## 🧰 Requirements

* 🐋 [Docker](https://docs.docker.com/get-docker/)

## 🎬 Usage

MKVresort requires 2 volumes to be mounted: `/app/input` and `/app/output`.

### 🐋 Docker

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest -h
```

### 🐳 Compose

Create a `compose.yaml` file.

```yaml
services:
  mkvresort:
    image: ghcr.io/toshy/mkvresort:latest
    volumes:
      - ./input:/input
      - ./output:/output
```

Then run it.

```shell
docker compose run -u $(id -u):$(id -g) --rm mkvresort -h
```

> [!NOTE]
> The `/app/preset` volume mount is optional.

> [!TIP]
> You can add additional JSON presets by mounting the files to the preset directory.
> ```yaml
> ./preset/custom.json:/app/preset/custom.json
> ```

## 🛠️ Contribute

### Requirements

* ☑️ [Pre-commit](https://pre-commit.com/#installation).
* 🐋 [Docker Compose V2](https://docs.docker.com/compose/install/)
* 📋 [Task 3.37+](https://taskfile.dev/installation/)

### Pre-commit

Setting up `pre-commit` code style & quality checks for local development.

```shell
pre-commit install
```

## ❕ License

This repository comes with a [MIT license](./LICENSE).
