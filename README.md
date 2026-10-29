---
title: ROICropper
emoji: 🌍
colorFrom: green
colorTo: pink
sdk: gradio
sdk_version: 6.31.0
app_file: app.py
pinned: false
license: mit
---

# ROICropper

Crop image objects from files or folders into any aspect ratio (1:1, 4:3, 16:9, etc.) focused on the main object against a white background.

[![PyPI version](https://img.shields.io/pypi/v/roicropper.svg)](https://pypi.org/project/roicropper/)
[![Python versions](https://img.shields.io/pypi/pyversions/roicropper.svg)](https://pypi.org/project/roicropper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Installation

Install core + CLI:

```bash
pip install roicropper
```

Install with optional features:

```bash
pip install roicropper[cli]    # CLI tools
pip install roicropper[web]    # Gradio web UI
pip install roicropper[dev]    # Testing and linting
pip install roicropper[cli,web]  # Everything
```

## Usage

### CLI

Single image crop:

```bash
roi-cropper crop input.jpg output.png --size 640 --aspect-ratio 1:1
```

Batch process:

```bash
roi-cropper batch ./input_folder/ ./output_folder/ --size 1280 --padding 15
```

Launch the web interface:

```bash
roi-cropper web
```

Open http://localhost:7860 in your browser.

Or run the standalone server directly:

```bash
roi-cropper-web
```

### Docker

Build and run:

```bash
docker build -t roicropper .
docker run -p 7860:7860 roicropper
```

## HuggingFace Spaces

This app is designed to run on [HuggingFace Spaces](https://huggingface.co/spaces) as a Gradio app. The root `app.py` launches the interface.

## Parameters

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--size` | `-s` | `int` | `640` | Output dimensions for square crop |
| `--max-size` | | `int` | `1280` | Maximum dimension for aspect crop |
| `--aspect-ratio` | `-a` | `str` | `1:1` | Aspect ratio, e.g. `16:9` |
| `--padding` | `-p` | `int` | `10` | Padding in pixels around object |
| `--format` | `-f` | `str` | `png` | Output format: jpg or png |
| `--host` | `-h` | `str` | `0.0.0.0` | Host to bind (web command) |
| `--port` | `-p` | `int` | `7860` | Port to listen on (web command) |

## Web Interface Features

- **Single crop**: Upload one image and preview the result instantly
- **Batch mode**: Upload multiple images, download all cropped results as a ZIP archive
- **Presets**: Quick-select common ratios (1:1, 4:3, 16:9, 3:2, A4)
- **Custom ratios**: Enter any width:height combination

## Development

### Setup

```bash
uv pip install -e '.[dev,cli,web]'
python -m pytest tests/ -v
```

### Adding Fixtures

Place sample images in `tests/fixtures/` for integration tests. Use common names like `sample.png`, `landscape.jpg`.

---

Built by [Fazri Gading](https://github.com/fazrigading/ROICropper) in 2026
