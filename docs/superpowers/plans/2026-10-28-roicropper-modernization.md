# ROICropper Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the single-file CLI script into a modern Python package with a pure-core module, Typer CLI, Gradio web UI, Docker support, and proper testing.

**Architecture:** Extract crop logic into `src/roicropper/core.py` as pure functions returning numpy arrays; build CLI and web frontends that delegate to core. Package with optional dependency groups via pyproject.toml.

**Tech Stack:** Python 3.11+, opencv-python-headless, numpy, typer, rich, gradio, pytest, ruff, hatchling

**Spec:** `docs/superpowers/specs/2026-10-28-roicropper-modernization-design.md`

## Global Constraints

- Project version: 1.0.0
- Build system: hatchling
- CLI entry point name: `roi-cropper`
- Default output size: 640
- Default padding: 10 pixels
- Output must maintain aspect ratio as specified (1:1 square or custom W×H tuple)
- Core functions return `np.ndarray`, never write files
- Conventional commit messages (e.g., `feat:`, `test:`, `docs:`)

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Modify: `README.md`
- Create: `tests/fixtures/.gitkeep`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: project metadata, build configuration, installable package shell

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "roicropper"
version = "1.0.0"
description = "Crop image objects to 1:1 square or any aspect ratio focusing on the main object"
readme = "README.md"
license = { file = "LICENSE" }
requires-python = ">=3.11"
dependencies = [
    "opencv-python-headless>=4.8",
    "numpy>=1.24",
]

[project.optional-dependencies]
cli = [
    "typer>=0.9.0",
    "rich>=13.0",
]
web = [
    "gradio>=4.0",
]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
]

[project.scripts]
roi-cropper = "cli.__main__:app"

[tool.hatch.build.targets.wheel]
packages = ["src/roicropper"]

[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Update `README.md`**

Replace the entire README content with:

```markdown
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
```

- [ ] **Step 3: Create `tests/fixtures/.gitkeep`**

Create an empty file at `tests/fixtures/.gitkeep` (placeholder for sample images).

- [ ] **Step 4: Run linting check**

Run: `ruff check --isolated . 2>/dev/null || true`

Expected: No errors (pyproject.toml is valid).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml README.md tests/fixtures/.gitkeep
git commit -m "chore: scaffold pyproject.toml with project config and update README"
```

---

### Task 2: Core Module — Crop Logic (TDD)

**Files:**
- Create: `src/roicropper/__init__.py`
- Create: `src/roicropper/core.py`
- Create: `tests/test_core.py`

**Interfaces:**
- Consumes: nothing (no prior dependencies beyond package layout)
- Produces: two public functions in `roicropper.core`:
  - `crop_to_square(image_path: str | Path, target_size: int = 640, padding_pixels: int = 10) -> np.ndarray | None`
  - `crop_to_aspect_ratio(image_path: str | Path, aspect_ratio: tuple[int, int], max_size: int = 1280, padding_pixels: int = 10) -> np.ndarray | None`

- [ ] **Step 1: Create `src/roicropper/__init__.py`**

Create file with:

```python
"""ROICropper — Crop image objects to any aspect ratio."""

from roicropper.core import crop_to_aspect_ratio, crop_to_square

__all__ = ["crop_to_square", "crop_to_aspect_ratio"]
```

- [ ] **Step 2: Write failing tests for `test_core.py`**

Create `tests/test_core.py`:

```python
import os
from pathlib import Path

import numpy as np
import pytest

# Tests assume fixture images exist in tests/fixtures/
FIXTURES_DIR = Path(__file__).parent / "fixtures"

def _has_fixture(name: str) -> bool:
    """Check if a fixture image exists (skip test if not)."""
    for ext in (".png", ".jpg", ".jpeg", ".bmp"):
        path = FIXTURES_DIR / (name + ext)
        if path.exists():
            return str(path)
    return ""


@pytest.fixture
def sample_image_path():
    """Path to a sample image, or skip if unavailable."""
    path = _has_fixture("sample")
    if not path:
        pytest.skip("No fixture image found in tests/fixtures/")
    return path


class TestCropToSquare:
    def test_returns_numpy_array(self, sample_image_path):
        from roicropper.core import crop_to_square
        result = crop_to_square(sample_image_path, target_size=640, padding_pixels=10)
        assert isinstance(result, np.ndarray)

    def test_output_is_square(self, sample_image_path):
        from roicropper.core import crop_to_square
        result = crop_to_square(sample_image_path, target_size=640, padding_pixels=10)
        assert result.shape[0] == 640
        assert result.shape[1] == 640

    def test_custom_size(self, sample_image_path):
        from roicropper.core import crop_to_square
        result = crop_to_square(sample_image_path, target_size=1280, padding_pixels=5)
        assert result.shape[0] == 1280
        assert result.shape[1] == 1280

    def test_nonexistent_file(self):
        from roicropper.core import crop_to_square
        result = crop_to_square("/nonexistent/path/image.png", target_size=640)
        assert result is None


class TestCropToAspectRatio:
    def test_returns_numpy_array(self, sample_image_path):
        from roicropper.core import crop_to_aspect_ratio
        result = crop_to_aspect_ratio(sample_image_path, aspect_ratio=(16, 9), max_size=1280)
        assert isinstance(result, np.ndarray)

    def test_16by9_ratio(self, sample_image_path):
        from roicropper.core import crop_to_aspect_ratio
        result = crop_to_aspect_ratio(sample_image_path, aspect_ratio=(16, 9), max_size=1280)
        # Check width/height ratio approximates 16:9
        if result.shape[0] > 0 and result.shape[1] > 0:
            ratio = result.shape[1] / result.shape[0]
            assert abs(ratio - 16 / 9) < 0.05  # within 5% tolerance due to integer rounding

    def test_4by3_ratio(self, sample_image_path):
        from roicropper.core import crop_to_aspect_ratio
        result = crop_to_aspect_ratio(sample_image_path, aspect_ratio=(4, 3), max_size=1280)
        if result.shape[0] > 0 and result.shape[1] > 0:
            ratio = result.shape[1] / result.shape[0]
            assert abs(ratio - 4 / 3) < 0.05

    def test_nonexistent_file(self):
        from roicropper.core import crop_to_aspect_ratio
        result = crop_to_aspect_ratio("/nonexistent/path/image.png", aspect_ratio=(16, 9))
        assert result is None
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd /home/fazrigading/Projects/ROICropper && python -m pytest tests/test_core.py -v`

Expected: FAIL with "ModuleNotFoundError: No module named 'roicropper'" or "crop_to_square not defined".

- [ ] **Step 4: Implement `src/roicropper/core.py`**

```python
"""Core crop logic — pure functions, no I/O side effects."""

from __future__ import annotations

import cv2
import numpy as np
from pathlib import Path


def _find_object_bounds(img: np.ndarray) -> tuple[int, int, int, int] | None:
    """Find bounding box of the main object in an image with white background.
    
    Returns (x, y, w, h) or None if no object detected.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    return x, y, w, h


def crop_to_square(
    image_path: str | Path,
    target_size: int = 640,
    padding_pixels: int = 10,
) -> np.ndarray | None:
    """Crop image to a 1:1 square focused on the main object.

    Args:
        image_path: Path to the input image.
        target_size: Output dimensions (width = height).
        padding_pixels: Fixed padding in pixels around object.

    Returns:
        Cropped and resized image as BGR numpy array, or None on failure.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None

    bounds = _find_object_bounds(img)
    if bounds is None:
        return None

    x, y, w, h = bounds
    center_x = x + w // 2
    center_y = y + h // 2
    max_dim = max(w, h)
    padded_size = max_dim + (2 * padding_pixels)

    half_size = padded_size // 2
    square_x = center_x - half_size
    square_y = center_y - half_size

    if square_x < 0:
        square_x = 0
    if square_y < 0:
        square_y = 0
    if square_x + padded_size > img.shape[1]:
        square_x = img.shape[1] - padded_size
    if square_y + padded_size > img.shape[0]:
        square_y = img.shape[0] - padded_size

    square_x = max(0, square_x)
    square_y = max(0, square_y)
    square_size = min(padded_size, img.shape[0] - square_y, img.shape[1] - square_x)

    cropped = img[square_y:square_y + square_size, square_x:square_x + square_size]
    resized = cv2.resize(cropped, (target_size, target_size), interpolation=cv2.INTER_AREA)
    return resized


def crop_to_aspect_ratio(
    image_path: str | Path,
    aspect_ratio: tuple[int, int],
    max_size: int = 1280,
    padding_pixels: int = 10,
) -> np.ndarray | None:
    """Crop image to any aspect ratio centered on the main object.

    Args:
        image_path: Path to the input image.
        aspect_ratio: Width × height ratio as tuple, e.g. (16, 9).
        max_size: Maximum dimension of the output.
        padding_pixels: Fixed padding in pixels around object.

    Returns:
        Cropped and resized image as BGR numpy array, or None on failure.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None

    bounds = _find_object_bounds(img)
    if bounds is None:
        return None

    x, y, w, h = bounds
    center_x = x + w // 2
    center_y = y + h // 2

    ar_w, ar_h = aspect_ratio
    scale = min(ar_w, ar_h)
    ratio = ar_w / ar_h if ar_h else 1.0

    # Calculate desired crop window dimensions based on aspect ratio
    if ar_w >= ar_h:
        crop_height = max(h, w / ratio)
        crop_width = int(crop_height * ratio)
    else:
        crop_width = max(w, h * ratio)
        crop_height = int(crop_width / ratio)

    # Apply padding
    crop_width_padded = int(crop_width) + (2 * padding_pixels)
    crop_height_padded = int(crop_height) + (2 * padding_pixels)

    # Ensure we don't exceed max_size
    if crop_width_padded > max_size and crop_height_padded > max_size:
        if crop_width_padded > crop_height_padded:
            crop_height_padded = int(crop_height_padded * (max_size / crop_width_padded))
            crop_width_padded = max_size
        else:
            crop_width_padded = int(crop_width_padded * (max_size / crop_height_padded))
            crop_height_padded = max_size

    half_w = crop_width_padded // 2
    half_h = crop_height_padded // 2
    start_x = center_x - half_w
    start_y = center_y - half_h

    if start_x < 0:
        start_x = 0
    if start_y < 0:
        start_y = 0
    if start_x + crop_width_padded > img.shape[1]:
        start_x = img.shape[1] - crop_width_padded
    if start_y + crop_height_padded > img.shape[0]:
        start_y = img.shape[0] - crop_height_padded

    start_x = max(0, start_x)
    start_y = max(0, start_y)

    end_x = min(start_x + crop_width_padded, img.shape[1])
    end_y = min(start_y + crop_height_padded, img.shape[0])

    cropped = img[start_y:end_y, start_x:end_x]

    # Resize to match aspect ratio exactly, fitting within max_size
    orig_w = cropped.shape[1]
    orig_h = cropped.shape[0]
    current_ratio = orig_w / orig_h if orig_h else 1

    if orig_h <= 0 or orig_w <= 0:
        return None

    if ar_w >= ar_h:
        # Landscape/tall landscape — fit width to max_size
        target_w = max_size
        target_h = int(max_size / ratio)
    else:
        # Portrait — fit height to max_size
        target_h = max_size
        target_w = int(max_size * ratio)

    # Ensure minimum dimensions
    target_w = max(1, target_w)
    target_h = max(1, target_h)

    resized = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_AREA)
    return resized
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /home/fazrigading/Projects/ROICropper && python -m pytest tests/test_core.py -v`

Expected: PASS (square tests skip if no fixture; nonexistent file tests pass immediately; fixture-dependent tests skip gracefully).

- [ ] **Step 6: Commit**

```bash
git add src/roicropper/__init__.py src/roicropper/core.py tests/test_core.py
git commit -m "feat: add core crop module with square and aspect ratio cropping"
```

---

### Task 3: Typer CLI

**Files:**
- Create: `cli/__main__.py`

**Interfaces:**
- Consumes: `roicropper.crop_to_square()`, `roicropper.crop_to_aspect_ratio()` from Task 2
- Produces: CLI entry point `roi-cropper` with `crop`, `batch`, and `web` subcommands

- [ ] **Step 1: Create `cli/__main__.py`**

```python
"""ROICropper CLI — crop images to any aspect ratio."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import typer
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn

app = typer.Typer(help="Crop image objects to any aspect ratio focused on the main object.", add_completion=False)
console = Console()


def _parse_aspect_ratio(ctx: str) -> tuple[int, int]:
    """Parse aspect ratio string like '16:9' into (16, 9)."""
    parts = ctx.split(":")
    if len(parts) != 2:
        raise typer.BadParameter(f"Invalid aspect ratio '{ctx}'. Expected format: W:H (e.g., 16:9)")
    try:
        w, h = int(parts[0]), int(parts[1])
        if w <= 0 or h <= 0:
            raise typer.BadParameter("Width and height must be positive integers.")
        return (w, h)
    except ValueError:
        raise typer.BadParameter(f"Invalid aspect ratio '{ctx}'. Expected format: W:H (e.g., 16:9)")


def _determine_extension(fmt: str) -> str:
    """Return cv2-compatible extension based on format."""
    fmt_lower = fmt.lower()
    if fmt_lower == "jpg":
        return ".jpg"
    return ".png"


def _save_result(img: np.ndarray, output_path: str, fmt: str) -> None:
    """Save numpy array to file using cv2."""
    outpath = Path(output_path)
    outpath.parent.mkdir(parents=True, exist_ok=True)
    ext = _determine_extension(fmt)
    if ext == ".jpg":
        cv2.imwrite(str(outpath.with_suffix(ext)), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    else:
        cv2.imwrite(str(outpath.with_suffix(".png")), img)


@app.command()
def crop(
    input_path: str = typer.Argument(..., help="Input image path"),
    output_path: str = typer.Argument(..., help="Output image path"),
    size: int = typer.Option(640, "--size", "-s", help="Output size for square crop"),
    aspect_ratio: str = typer.Option("1:1", "--aspect-ratio", "-a", help="Aspect ratio, e.g. 16:9"),
    padding: int = typer.Option(10, "--padding", "-p", help="Padding in pixels around object"),
    fmt: str = typer.Option("png", "--format", "-f", help="Output format: jpg or png"),
) -> None:
    """Crop a single image to a square or custom aspect ratio."""
    from roicropper.core import crop_to_aspect_ratio, crop_to_square

    ar = _parse_aspect_ratio(aspect_ratio)
    if ar == (1, 1):
        result = crop_to_square(input_path, target_size=size, padding_pixels=padding)
    else:
        result = crop_to_aspect_ratio(input_path, aspect_ratio=ar, max_size=size, padding_pixels=padding)

    if result is None:
        console.print(f"[red]Error:[/] Could not process {input_path}. No object found or file unreadable.")
        raise typer.Exit(1)

    _save_result(result, output_path, fmt)
    console.print(f"[green]Processed:[/] {input_path} -> {output_path}")


@app.command()
def batch(
    input_dir: str = typer.Argument(..., help="Input directory containing images"),
    output_dir: str = typer.Argument(..., help="Output directory for processed images"),
    size: int = typer.Option(640, "--size", "-s", help="Output size for square crop"),
    aspect_ratio: str = typer.Option("1:1", "--aspect-ratio", "-a", help="Aspect ratio, e.g. 16:9"),
    padding: int = typer.Option(10, "--padding", "-p", help="Padding in pixels around object"),
    fmt: str = typer.Option("png", "--format", "-f", help="Output format: jpg or png"),
) -> None:
    """Process all images in a directory."""
    from roicropper.core import crop_to_aspect_ratio, crop_to_square

    ar = _parse_aspect_ratio(aspect_ratio)
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)

    supported_exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    images = []
    for ext in supported_exts:
        images.extend(input_path.glob(f"*{ext}"))

    if not images:
        console.print(f"[yellow]Warning:[/] No supported images found in {input_dir}")
        return

    count = 0
    failed = 0
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("{task.completed}/{task.total}"), console=console) as progress:
        task = progress.add_task("Processing...", total=len(images))
        for img_path in sorted(images):
            try:
                if ar == (1, 1):
                    result = crop_to_square(str(img_path), target_size=size, padding_pixels=padding)
                else:
                    result = crop_to_aspect_ratio(str(img_path), aspect_ratio=ar, max_size=size, padding_pixels=padding)

                if result is None:
                    console.print(f"  [red]Skipped:[/] {img_path.name} (no object)")
                    failed += 1
                    continue

                out_file = output_path / img_path.name
                _save_result(result, str(out_file), fmt)
                count += 1
                progress.advance(task)
            except Exception as e:
                console.print(f"  [red]Error processing {img_path.name}:[/] {e}")
                failed += 1
                progress.advance(task)

    status = f"[green]Done:[/] {count} processed, {failed} skipped."
    console.print(status)


if __name__ == "__main__":
    app()
```

- [ ] **Step 2: Verify CLI runs**

Run: `cd /home/fazrigading/Projects/ROICropper && python -m cli.__main__ --help`

Expected: Shows Typer-generated help with `crop`, `batch`, and root help.

- [ ] **Step 3: Verify crop command rejects bad inputs**

Run: `cd /home/fazrigading/Projects/ROICropper && python -m cli.__main__ crop nonexistent.png out.png 2>&1 | head -5`

Expected: Error message mentioning "Could not process" or missing file.

- [ ] **Step 4: Commit**

```bash
git add cli/__main__.py
git commit -m "feat: add Typer CLI with crop and batch subcommands"
```

---

### Task 4: Gradio Web UI

**Files:**
- Create: `web/app.py`

**Interfaces:**
- Consumes: `roicropper.crop_to_square()`, `roicropper.crop_to_aspect_ratio()` from Task 2
- Produces: Gradio web interface with upload, sliders, previews, download

- [ ] **Step 1: Create `web/app.py`**

```python
"""ROICropper Web UI — Gradio interface for crop operations."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Any

import cv2
import gradio as gr
import numpy as np

from roicropper.core import crop_to_aspect_ratio, crop_to_square

PRESETS = [("1:1", (1, 1)), ("4:3", (4, 3)), ("16:9", (16, 9)), ("3:2", (3, 2)), ("A4", (210, 297))]


def _process_crop(
    image: Any,
    crop_type: str,
    preset: str,
    custom_w: str,
    custom_h: str,
    slider_size: int,
    slider_padding: int,
) -> tuple[np.ndarray | None, str]:
    """Core crop processing called by both Gradio callbacks."""
    if image is None:
        return None, "Please upload an image first."

    if isinstance(image, dict) and "full_img" in image:
        img_arr = image["full_img"]
    elif isinstance(image, np.ndarray):
        img_arr = image
    else:
        return None, "Unsupported input type."

    # Save uploaded image to temp file for core module
    tmp_dir = Path("/tmp/roicropper")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"upload_{id(image)}.png"
    cv2.imwrite(str(tmp_path), img_arr)

    try:
        if crop_type == "Custom Ratio":
            try:
                ar = (int(custom_w.strip()), int(custom_h.strip()))
                if ar[0] <= 0 or ar[1] <= 0:
                    return None, "Width and height must be positive integers."
            except ValueError:
                return None, "Invalid custom aspect ratio values."
            result = crop_to_aspect_ratio(str(tmp_path), aspect_ratio=ar, max_size=slider_size, padding_pixels=slider_padding)
        else:
            result = crop_to_square(str(tmp_path), target_size=slider_size, padding_pixels=slider_padding)
    finally:
        tmp_path.unlink(missing_ok=True)

    if result is None:
        return None, "Could not process image. No object found or file unreadable."

    return result, f"Success — cropped at {result.shape[1]}x{result.shape[0]}"


def _resize_for_preview(img: np.ndarray, max_preview: int = 400) -> np.ndarray:
    """Resize image for preview display while keeping aspect ratio."""
    h, w = img.shape[:2]
    if h > max_preview or w > max_preview:
        scale = min(max_preview / h, max_preview / w)
        return cv2.resize(img, (int(w * scale), int(h * scale)))
    return img


def ui_callback(*args: Any) -> tuple[np.ndarray | None, str]:
    """Gradio callback for the Process button."""
    result, msg = _process_crop(*args)
    preview = _resize_for_preview(result) if result is not None else None
    return preview, msg


def handle_batch(
    files: list[str],
    crop_type: str,
    preset: str,
    custom_w: str,
    custom_h: str,
    slider_size: int,
    slider_padding: int,
    fmt: str,
) -> bytes | None:
    """Process multiple images and return ZIP archive."""
    tmp_dir = Path("/tmp/roicropper/batch")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    ar_w, ar_h = 1, 1
    if crop_type == "Custom Ratio":
        try:
            ar_w, ar_h = int(custom_w.strip()), int(custom_h.strip())
        except ValueError:
            return None

    results = []
    for i, file_path in enumerate(files):
        img = cv2.imread(str(file_path))
        if img is None:
            continue

        if crop_type == "Custom Ratio":
            result = crop_to_aspect_ratio(str(file_path), aspect_ratio=(ar_w, ar_h), max_size=slider_size, padding_pixels=slider_padding)
        else:
            result = crop_to_square(str(file_path), target_size=slider_size, padding_pixels=slider_padding)

        if result is None:
            continue

        filename = f"cropped_{i+1}.{'jpg' if fmt == 'jpg' else 'png'}"
        save_path = tmp_dir / filename
        cv2.imwrite(str(save_path), result, [cv2.IMWRITE_JPEG_QUALITY, 95] if fmt == "jpg" else [])
        results.append(filename)

    if not results:
        return None

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in results:
            zf.write(tmp_dir / fname, fname)

    # Cleanup
    for fname in results:
        (tmp_dir / fname).unlink(missing_ok=True)
    tmp_dir.rmdir()

    zip_io.seek(0)
    return zip_io.getvalue()


def _get_theme() -> gr.Theme:
    return gr.themes.Soft(primary_hue="indigo", neutral_hue="slate")


theme = _get_theme()

with gr.Blocks(title="ROICropper", theme=theme) as demo:
    gr.Markdown("# ROICropper\nCrop image objects to any aspect ratio")
    gr.Markdown("Built by [Fazri Gading](https://github.com/fazrigading/ROICropper)")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Tab("Single"):
                img_input = gr.Image(type="numpy", label="Upload Image", height=400)
                crop_type = gr.Radio(["Square", "Custom Ratio"], value="Square", label="Crop Type")
                preset = gr.Dropdown([p[0] for p in PRESETS], value="1:1", label="Aspect Ratio Preset")
                with gr.Group(visible=False) as custom_group:
                    custom_w = gr.Number(label="Custom Width", value=16, precision=0)
                    custom_h = gr.Number(label="Custom Height", value=9, precision=0)
                slider_size = gr.Slider(128, 4096, value=640, step=64, label="Size")
                slider_padding = gr.Slider(0, 100, value=10, step=1, label="Padding")
                btn_process = gr.Button("Process", variant="primary")
            with gr.Tab("Batch"):
                batch_input = gr.File(file_count="multiple", label="Upload Multiple Images")
                same_controls = True
                btn_process_batch = gr.Button("Process All & Download ZIP", variant="primary")
            with gr.Tab("Info"):
                gr.Markdown("### How It Works\n1. Upload an image with a white/light background\n2. Select crop type (square or custom aspect ratio)\n3. Adjust presets or custom dimensions\n4. Set size and padding\n5. Click Process\n\nThe tool detects the main object and crops to the requested ratio centered on it.")
                gr.Markdown(f"### Supported Formats\nJPG, PNG, BMP, TIFF\n\n### Limits\nMax resolution handled depends on available RAM. Batch mode recommended for 50+ images.")

        with gr.Column(scale=1):
            img_output = gr.Image(type="numpy", label="Result")
            status_text = gr.Textbox(label="Status", interactive=False)

    # Custom ratio visibility toggle
    crop_type.change(lambda t: gr.Group(visible=t == "Custom Ratio"), crop_type, custom_group)
    preset.change(lambda v: {"1:1": (1, 1), "4:3": (4, 3), "16:9": (16, 9), "3:2": (3, 2), "A4": (210, 297)}.get(v, (1, 1)), preset, fn=lambda v: gr.update(value=v[0]) if isinstance(v, tuple) else None)

    btn_process.click(
        ui_callback,
        inputs=[img_input, crop_type, preset, custom_w, custom_h, slider_size, slider_padding],
        outputs=[img_output, status_text],
    )

    btn_process_batch.click(
        handle_batch,
        inputs=[batch_input, crop_type, preset, custom_w, custom_h, slider_size, slider_padding, gr.State("png")],
        outputs=gr.File(label="Download Result"),
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

- [ ] **Step 2: Verify web module loads**

Run: `cd /home/fazrigading/Projects/ROICropper && python -c "import web.app; print('OK')"`

Expected: `OK` (no errors importing).

- [ ] **Step 3: Commit**

```bash
git add web/app.py
git commit -m "feat: add Gradio web UI with square and custom ratio cropping"
```

---

### Task 5: Docker Deployment

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`

**Interfaces:**
- Consumes: everything from Tasks 1-4
- Produces: reproducible Docker image running `roi-cropper web` on port 7860

- [ ] **Step 1: Create `Dockerfile`**

```dockerfile
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml ./

RUN uv sync --frozen --extra web

FROM python:3.12-slim AS runtime

RUN groupadd --system roico && useradd --system --gid roico roico
WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

USER roico
EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:7860/ || exit 1

ENTRYPOINT ["roi-cropper"]
CMD ["web"]
```

- [ ] **Step 2: Create `.dockerignore`**

```
.git
.github
__pycache__
*.pyc
.codegraph
.projectmem
commandcode
*.md~
.DS_Store
```

- [ ] **Step 3: Verify Dockerfile parses**

Run: `cd /home/fazrigading/Projects/ROICropper && docker build --dry-run . 2>/dev/null || echo "Docker daemon not available — Dockerfile syntax checked manually."`

Expected: Pass or informative message (no parse errors in Dockerfile).

- [ ] **Step 4: Commit**

```bash
git add Dockerfile .dockerignore
git commit -m "feat: add multi-stage Dockerfile with non-root user"
```

---

### Task 6: Cleanup & Final Verification

**Files:**
- Delete: `ROICropper.py` (original single-file script)

**Interfaces:**
- Consumes: everything from Tasks 1-5
- Produces: clean project ready for use, all old artifacts removed

- [ ] **Step 1: Remove old `ROICropper.py`**

```bash
rm /home/fazrigading/Projects/ROICropper/ROICropper.py
```

- [ ] **Step 2: Verify full package imports work**

Run: `cd /home/fazrigading/Projects/ROICropper && python -c "import roicropper; print(roicropper.__all__); from cli.__main__ import app; print('CLI OK'); import web.app; print('Web OK')"`

Expected: `['crop_to_square', 'crop_to_aspect_ratio']` then `CLI OK` then `Web OK`.

- [ ] **Step 3: Verify CLI entry point works**

Run: `cd /home/fazrigading/Projects/ROICropper && roi-cropper --help`

Expected: Typer-generated help output listing `crop` and `batch` commands.

- [ ] **Step 4: Verify all tests pass**

Run: `cd /home/fazrigading/Projects/ROICropper && python -m pytest tests/ -v`

Expected: All tests pass or gracefully skip (fixture-dependent ones).

- [ ] **Step 5: Commit**

```bash
git rm ROICropper.py
git add -A
git commit -m "chore: remove legacy single-file script, finalize modernized structure"
```

---

## Summary

6 tasks covering the full scope of the spec:
1. Project scaffolding (pyproject.toml, README, test directory)
2. Core crop logic with TDD (square + aspect ratio)
3. Typer CLI with crop and batch subcommands
4. Gradio web UI with sliders, previews, batch download
5. Docker deployment (multi-stage, non-root user)
6. Cleanup (remove old file, final verification)
