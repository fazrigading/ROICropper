# ROICropper

Crop image objects from files or folders into any aspect ratio (1:1, 4:3, 16:9, etc.) focused on the main object against a white background.

## Installation

Install core + CLI:
```bash
pip install roicropper
```

Install with web UI:
```bash
pip install roicropper[web]
```

Install with dev tools:
```bash
pip install roicropper[dev]
```

## Usage

### CLI

Single image:
```bash
roi-cropper crop input.jpg output.png --size 640 --aspect-ratio 1:1
```

Batch process:
```bash
roi-cropper batch ./input_folder/ ./output_folder/ --size 1280 --padding 15
```

Web UI:
```bash
roi-cropper web
```

Open http://localhost:7860 in your browser.

### Docker

Build and run:
```bash
docker build -t roicropper .
docker run -p 7860:7860 roicropper
```

## Parameters

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--size`, `-s` | | `int` | `640` | Output dimensions for square crop |
| `--max-size` | | `int` | `1280` | Maximum dimension for aspect crop |
| `--aspect-ratio`, `-a` | | `str` | `1:1` | Aspect ratio, e.g. `16:9` |
| `--padding`, `-p` | | `int` | `10` | Padding in pixels around object |
| `--format`, `-f` | | `str` | `png` | Output format: jpg or png |

Built by [Fazri Gading](https://github.com/fazrigading/ROICropper)
