"""Core crop logic — pure functions, no I/O side effects."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


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

    square_x = max(square_x, 0)
    square_y = max(square_y, 0)
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

    start_x = max(start_x, 0)
    start_y = max(start_y, 0)
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

    if orig_h <= 0 or orig_w <= 0:
        return None

    if ar_w >= ar_h:
        # Landscape — fit width to max_size
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
