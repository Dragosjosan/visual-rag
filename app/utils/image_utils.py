import base64
from io import BytesIO
from typing import Tuple

from loguru import logger
from PIL import Image


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    try:
        buffer = BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as exc:
        logger.opt(exception=exc).error("Failed to convert image to base64")
        raise ValueError(f"Failed to convert image to base64: {exc}") from exc


def resize_image(
    image: Image.Image,
    max_width: int | None = None,
    max_height: int | None = None,
    maintain_aspect_ratio: bool = True,
) -> Image.Image:
    if max_width is not None and max_width <= 0:
        raise ValueError(f"max_width must be positive, got {max_width}")
    if max_height is not None and max_height <= 0:
        raise ValueError(f"max_height must be positive, got {max_height}")

    if max_width is None and max_height is None:
        return image

    try:
        original_width, original_height = image.size

        if maintain_aspect_ratio:
            if max_width and max_height:
                ratio = min(max_width / original_width, max_height / original_height)
            elif max_width:
                ratio = max_width / original_width
            else:
                ratio = max_height / original_height

            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
        else:
            new_width = max_width if max_width else original_width
            new_height = max_height if max_height else original_height

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    except Exception as exc:
        logger.opt(exception=exc).error("Failed to resize image")
        raise ValueError(f"Failed to resize image: {exc}") from exc


def get_image_dimensions(image: Image.Image) -> Tuple[int, int]:
    try:
        return image.size
    except Exception as exc:
        logger.opt(exception=exc).error("Failed to get image dimensions")
        raise ValueError(f"Failed to get image dimensions: {exc}") from exc
