## Usage

The following section shows the basic presets that are already available. You
can add your custom presets by mounting files to the `/app/preset` directory.

---

### 🐋 Docker

```shell
docker run -it --rm \
  -u $(id -u):$(id -g) \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  -v ${PWD}/preset/order-custom.json:/app/preset/order-custom.json \
  ghcr.io/toshy/mkvresort:latest
```

### 🐳 Compose

```yaml
services:
  mkvresort:
    image: ghcr.io/toshy/mkvresort:latest
    volumes:
      - ./input:/app/input
      - ./output:/app/output
      - ./preset/order-custom.json:/app/preset/order-custom.json
```

## Style

Argument: `--preset` / `-p`.

---

### Default

The default preset will sort streams in descending order (`false`) for the given stream properties `language` and `track_name`.

???+ example "`default.json`"

    ```json
    {
        "language": false,
        "track_name": false
    }
    ```

### Custom

To reverse the ordering (from descending to ascending), you can supply a custom preset and change the value for the given properties from `false` to `true`. 

```json
{
    "language": true,
    "track_name": true
}
```
