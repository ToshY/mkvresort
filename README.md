<h1 align="center"> 📺 MKVresort </h1>

<div align="center">
    <img src="https://img.shields.io/github/v/release/toshy/mkvresort?label=Release&sort=semver" alt="Current bundle version" />
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/codestyle.yml?branch=main&label=Black" alt="Black">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/codequality.yml?branch=main&label=Ruff" alt="Ruff">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/statictyping.yml?branch=main&label=Mypy" alt="Mypy">
    <img src="https://img.shields.io/github/actions/workflow/status/toshy/mkvresort/security.yml?branch=main&label=Security%20check" alt="Security check" />
    <br /><br />
    <div>A command-line utility for resorting video, audio and subtitle streams.</div>
</div>

## 📝 Quickstart

```sh
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest -h
```

## 📜 Documentation

The documentation is available at [https://toshy.github.io/mkvresort](https://toshy.github.io/mkvresort).

## 🛠️ Contribute

### Requirements

* ☑️ [Pre-commit](https://pre-commit.com/#installation).
* 🐋 [Docker Compose V2](https://docs.docker.com/compose/install/)
* 📋 [Task 3.37+](https://taskfile.dev/installation/)

## ❕ License

This repository comes with a [MIT license](./LICENSE).
