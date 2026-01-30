import base64
from io import BytesIO

import pytest
from PIL import Image

from src.utils.image_utils import (
    get_image_dimensions,
    image_to_base64,
    resize_image,
)


@pytest.fixture
def sample_image():
    image = Image.new("RGB", (800, 600), color=(255, 0, 0))
    return image


def test_image_to_base64(sample_image):
    result = image_to_base64(sample_image, format="PNG")

    assert isinstance(result, str)
    assert len(result) > 0

    decoded = base64.b64decode(result)
    reconstructed = Image.open(BytesIO(decoded))
    assert reconstructed.size == sample_image.size
    assert reconstructed.mode == sample_image.mode


def test_image_to_base64_different_format(sample_image):
    result = image_to_base64(sample_image, format="JPEG")

    assert isinstance(result, str)
    assert len(result) > 0


def test_resize_image_with_max_width(sample_image):
    resized = resize_image(sample_image, max_width=400)

    assert resized.size == (400, 300)
    assert resized.mode == "RGB"


def test_resize_image_with_max_height(sample_image):
    resized = resize_image(sample_image, max_height=300)

    assert resized.size == (400, 300)
    assert resized.mode == "RGB"


def test_resize_image_with_both_dimensions(sample_image):
    resized = resize_image(sample_image, max_width=400, max_height=200)

    assert resized.size[0] <= 400
    assert resized.size[1] <= 200
    assert resized.mode == "RGB"


def test_resize_image_no_resize(sample_image):
    resized = resize_image(sample_image)

    assert resized.size == sample_image.size


def test_resize_image_invalid_width(sample_image):
    with pytest.raises(ValueError, match="max_width must be positive"):
        resize_image(sample_image, max_width=-100)


def test_resize_image_invalid_height(sample_image):
    with pytest.raises(ValueError, match="max_height must be positive"):
        resize_image(sample_image, max_height=0)


def test_get_image_dimensions(sample_image):
    width, height = get_image_dimensions(sample_image)

    assert width == 800
    assert height == 600
