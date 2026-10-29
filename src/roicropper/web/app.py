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
        return cv2.resize(img, (int(w * scale), (h * scale)))
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

with gr.Blocks(title="ROICropper") as demo:
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
                gr.Markdown("### Supported Formats\nJPG, PNG, BMP, TIFF\n\n### Limits\nMax resolution handled depends on available RAM. Batch mode recommended for 50+ images.")

        with gr.Column(scale=1):
            img_output = gr.Image(type="numpy", label="Result")
            status_text = gr.Textbox(label="Status", interactive=False)

    # Custom ratio visibility toggle
    def _show_custom(crop_type_val):
        return gr.Group(visible=crop_type_val == "Custom Ratio")

    crop_type.change(_show_custom, crop_type, custom_group)

    # Preset values lookup
    PRESET_MAP = {"1:1": (1, 1), "4:3": (4, 3), "16:9": (16, 9), "3:2": (3, 2), "A4": (210, 297)}

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


def launch(server_name: str = "0.0.0.0", server_port: int = 7860) -> None:
    """Launch the Gradio web UI."""
    print(f"ROICropper web UI starting at http://{server_name}:{server_port}")
    demo.launch(server_name=server_name, server_port=server_port, theme=theme)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=theme)
