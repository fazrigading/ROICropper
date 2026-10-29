"""ROICropper CLI — crop images to any aspect ratio."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

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
            except OSError as e:
                console.print(f"  [red]Error processing {img_path.name}:[/] {e}")
                failed += 1
                progress.advance(task)

    status = f"[green]Done:[/] {count} processed, {failed} skipped."
    console.print(status)


@app.command()
def web(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(7860, "--port", "-p", help="Port to listen on"),
) -> None:
    """Launch the Gradio web interface."""
    import importlib.util

    if importlib.util.find_spec("gradio") is None:
        console.print("[red]Error:[/] Gradio is not installed. Run: pip install 'roicropper[web]'")
        raise typer.Exit(1)

    from roicropper.web import launch

    console.print(f"[green]Starting:[/] ROICropper web UI at http://{host}:{port}")
    launch(server_name=host, server_port=port)


if __name__ == "__main__":
    app()
