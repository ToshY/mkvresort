# Examples

## Basic

Add your files to the input directory of the mounted container.

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest
```

By default, it will find all files from the `/app/input` directory (recursively) and write the output to the `/app/output`
directory. If no presets are provided, it will automatically use the [`preset/default.json`](presets.md#default)

## Specific file

Resorting streams for a specific file and writing output to `/app/output` (default).

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/rick-astley-never-gonna-give-you-up.mkv"
```

## Single file with output subdirectory

Resorting streams for a specific file and writing output to `/app/output/hits`.

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/rick-astley-never-gonna-give-you-up.mkv" \
  -o "output/hits"
```

## Specific subdirectory

Resorting streams for files in a specific subdirectory and writing output to `/app/output/hits`.

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/hits" \
  -o "output/hits"
```

## Multiple inputs

Resorting streams for files in multiple input subdirectories and writing output to `/app/output` (default).

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/dir1" \
  -i "input/dir2" \
  -i "input/dir3" \
  -i "input/dir4" \
  -i "input/dir5"
```

## Multiple inputs and outputs

Resorting streams for files in multiple input subdirectories and writing output to specific output subdirectories
respectively.

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/dir1" \
  -i "input/dir2" \
  -i "input/dir3" \
  -i "input/dir4" \
  -i "input/dir5" \
  -o "output/dir1" \
  -o "output/dir2" \
  -o "output/dir3" \
  -o "output/dir4" \
  -o "output/dir5"
```

## Multiple inputs, outputs and single preset

Resorting streams for files in multiple input subdirectories, with a single custom preset, and writing output
to specific output subdirectories respectively.

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/dir1" \
  -i "input/dir2" \
  -i "input/dir3" \
  -i "input/dir4" \
  -i "input/dir5" \
  -p "preset/order-custom.json" \
  -o "output/dir1" \
  -o "output/dir2" \
  -o "output/dir3" \
  -o "output/dir4" \
  -o "output/dir5"
```

## Multiple inputs, outputs and presets

Resorting streams for files in multiple input subdirectories, with different presets, and writing output to specific
output subdirectories respectively.

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  -v ${PWD}/preset/video-custom.json:/app/preset/video-custom.json \
  -v ${PWD}/preset/audio-custom.json:/app/preset/audio-custom.json \
  ghcr.io/toshy/mkvresort:latest \
  -i "input/dir1" \
  -i "input/dir2" \
  -i "input/dir3" \
  -i "input/dir4" \
  -i "input/dir5" \
  -p "preset/order-custom.json" \
  -p "preset/order-custom-two.json" \
  -p "preset/order-custom-three.json" \
  -p "preset/order-custom-four.json" \
  -p "preset/order-custom.json" \
  -o "output/dir1" \
  -o "output/dir2" \
  -o "output/dir3" \
  -o "output/dir4" \
  -o "output/dir5"
```
