# ROICropper Modernization Design

**Date:** 2026-10-28
**Status:** Draft — pending user review

## Overview

Revamp ROICropper from a single-file CLI script into a modern Python package with two frontends: a structured CLI and a Gradio web UI. The core crop algorithm remains the same; everything else gets restructured for clarity, testability, and distribution flexibility.

## Project Structure

```
ROICropper/
├── pyproject.toml
├── README.md
├── Dockerfile
├── .dockerignore
└── src/
│   └── roicropper/
│       ├── __init__.py    # public API exports
│       └── core.py        # pure crop logic (no CLI/GUI deps)
│   ├── cli/__main__.py    # Typer CLI entry point
│   └── web/app.py         # Gradio frontend
└── tests/
    ├── test_core.py       # unit tests for crop algorithm
    └── fixtures/          # sample images for testing
```

The `src/` layout separates source from tests, following [packaging best practices](https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/#let-installers-decide-which-dependencies-to-install).

## Core Module (`roicropper/core.py`)

Two functions, no side effects:

### `crop_to_square(image_path: str | Path, target_size: int = 640, padding_pixels: int = 10) -> np.ndarray`

Crops image to a 1:1 square focused on the main object against a white background.

Parameters:
| Name             | Type            | Default | Description                     |
|------------------|-----------------|---------|---------------------------------|
| `image_path`     | `str \| Path`   | required| Input image file path            |
| `target_size`    | `int`           | `640`   | Output dimensions (width = height) |
| `padding_pixels` | `int`           | `10`    | Fixed padding in pixels around object |

Returns: `np.ndarray` — cropped and resized image as BGR numpy array.

### `crop_to_aspect_ratio(image_path: str | Path, aspect_ratio: tuple[int, int], max_size: int = 1280, padding_pixels: int = 10) -> np.ndarray`

Crops image to any aspect ratio (e.g., 16:9, 4:3, 3:2) centered on the main object.

Parameters:
| Name             | Type                  | Default | Description                              |
|------------------|-----------------------|---------|------------------------------------------|
| `image_path`     | `str \| Path`         | required| Input image file path                    |
| `aspect_ratio`   | `tuple[int, int]`     | required| Width × height ratio, e.g. `(16, 9)`     |
| `max_size`       | `int`                 | `1280`  | Maximum dimension of output              |
| `padding_pixels` | `int`                 | `10`    | Fixed padding in pixels around object    |

Returns: `np.ndarray` — cropped and resized image as BGR numpy array.

Both functions:
- Detect object contours via grayscale thresholding (non-white pixels)
- Use bounding rectangle centered on largest contour
- Respect image boundaries (no negative coordinates, no overflow)
- Validate input: return `None` or raise `ValueError` if file is missing/unreadable/no object found

CLI and web layers handle I/O, saving, and presentation — not the core logic.

## CLI (`cli/__main__.py`)

Typer-based CLI with subcommands:

### Commands

- `roi-cropper crop <input> <output>` — single image crop
- `roi-cropper batch <input_dir> <output_dir>` — process all supported images in a directory

### Flags

| Flag               | Short | Type   | Default | Description                        |
|--------------------|-------|--------|---------|------------------------------------|
| `--size`, `-s`     |       | `int`  | `640`   | Output size (for square crop)      |
| `--max-size`       |       | `int`  | `1280`  | Max dimension (for aspect crop)    |
| `--aspect-ratio`   | `-a`  | `str`  | `1:1`   | Aspect ratio, e.g. `16:9`          |
| `--padding`, `-p`  |       | `int`  | `10`    | Padding in pixels                  |
| `--format`         | `-f`  | `str`  | `png`   | Output format: jpg, png            |

### Features

- Progress bar via Rich during batch processing
- Colorized success/error messages
- Auto-generated help pages
- Structured error messages (missing files, unsupported formats, invalid paths)
- Version flag via `pyproject.toml` metadata

Both commands delegate to `roicropper.core` functions. No business logic in the CLI layer.

## Web UI (`web/app.py`)

Gradio interface built on a `gr.Blocks` layout:

### Components

- **Upload area**: drag-and-drop for single or batch image upload
- **Controls panel**:
  - Crop type selector: dropdown (Square / Custom Ratio)
  - Aspect ratio selector: dropdown with presets (1:1, 4:3, 16:9, 3:2, A4) + custom W×H text field when "Custom" selected
  - Size slider: range input for output dimensions
  - Padding slider: range input for padding in pixels
  - Format selector: dropdown (PNG/JPG)
- **Preview panels**: original vs cropped, side-by-side
- **Action buttons**: process, download (single file or ZIP archive)
- **Footer**: "Built by Fazri Gading" with GitHub icon/link

### Behavior

- Sliders update preview live on change (thumbnail-level first pass)
- Process button triggers actual crop at full resolution
- Batch mode shows progress indicator with completion summary
- Dark/light theme toggle via Gradio theme prop

All crop logic delegates to `roicropper.core`. Web layer handles presentation, state, and downloads only.

## Packaging (`pyproject.toml`)

| Dependency group | Contents                          | When needed              |
|------------------|-----------------------------------|--------------------------|
| Core             | `opencv-python-headless`, `numpy` | Always                   |
| CLI              | `typer>=0.9.0`, `rich>=13.0`      | CLI usage                |
| Web              | `gradio>=4.0`                     | Web UI usage             |
| Dev              | `pytest`, `pytest-cov`, `ruff`    | Development              |

Entry point: `roi-cropper = "cli.__main__:app"` (Typer CLI invocation).

Install variants:
- `pip install roicropper` → core + CLI
- `pip install roicropper[web]` → adds Gradio web UI
- `pip install roicropper[dev]` → development tools
- `uv pip install roicropper --all-extras` → everything

Build system: `hatchling`. Version: `1.0.0`.

## Deployment

| Mode     | Method                                    | Port | Notes                            |
|----------|-------------------------------------------|------|----------------------------------|
| Local    | `pip install roicropper` + CLI commands   | N/A  | Standard package installation    |
| Local Web| `roi-cropper web`                         | 7860 | Starts Gradio dev server locally |
| Docker   | Multi-stage build from `python:slim`      | 7860 | Non-root user, `EXPOSE 7860`     |
| Vercel   | `vercel.json` config                      | 443  | Route proxy to Gradio backend    |

Dockerfile: multi-stage build, non-root user, health check on port 7860, `CMD ["roi-cropper", "web"]`.

Vercel: lightweight FastAPI route that proxies requests to Gradio's internal server, or alternatively deploy via HuggingFace Spaces (native Gradio hosting).

CI (GitHub Actions): Ruff linting + formatting, pytest run on every PR push.

## Testing

Unit tests for `core.py` in `tests/test_core.py`:

- Square crop: verify output dimensions match `target_size`
- Aspect ratio crop: verify output width/height ratio matches requested aspect ratio
- Boundary handling: test with small images, images where crop would overflow
- Edge cases: image with no detectable object (white-only input), corrupted files
- Snapshot tests: compare outputs against known-good reference images in `tests/fixtures/`

Tests call `roicropper.core` directly. No Gradio or Typer dependencies required. Coverage threshold enforced via `pytest-cov`.
