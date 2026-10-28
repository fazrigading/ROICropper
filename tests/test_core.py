from pathlib import Path

import numpy as np
import pytest

# Tests assume fixture images exist in tests/fixtures/
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _has_fixture(name: str) -> str:
    """Check if a fixture image exists, return path or empty string."""
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
