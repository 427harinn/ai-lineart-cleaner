"""Reusable image processing for black-line-on-white line art."""

import re

import cv2
import numpy as np

DEFAULT_THRESHOLD = 80
DEFAULT_LINE_COLOR = "#000000"


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Return grayscale pixels, compositing BGRA transparency over white."""
    if image.ndim == 2:
        return image
    if image.ndim != 3:
        raise ValueError("Unsupported image format.")
    if image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if image.shape[2] == 4:
        bgr = image[:, :, :3].astype(np.float32)
        alpha = image[:, :, 3:4].astype(np.float32) / 255.0
        composited = bgr * alpha + 255.0 * (1.0 - alpha)
        return cv2.cvtColor(composited.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    raise ValueError("Unsupported number of image channels.")


def extract_lineart(image: np.ndarray, threshold: int = DEFAULT_THRESHOLD) -> np.ndarray:
    """Make pixels at or below *threshold* black and the rest white."""
    if not 0 <= threshold <= 255:
        raise ValueError("Threshold must be between 0 and 255.")
    grayscale = to_grayscale(image)
    _, lineart = cv2.threshold(grayscale, threshold, 255, cv2.THRESH_BINARY)
    return lineart


def parse_line_color(line_color: str = DEFAULT_LINE_COLOR) -> tuple[int, int, int]:
    """Validate a ``#RRGGBB`` color and return it as an RGB tuple."""
    if not isinstance(line_color, str) or re.fullmatch(r"#[0-9A-Fa-f]{6}", line_color) is None:
        raise ValueError("Line color must use the #RRGGBB format.")
    try:
        red = int(line_color[1:3], 16)
        green = int(line_color[3:5], 16)
        blue = int(line_color[5:7], 16)
    except ValueError as error:
        raise ValueError("Line color must use the #RRGGBB format.") from error
    return red, green, blue


def colorize_lineart(
    lineart: np.ndarray, line_color: tuple[int, int, int] = (0, 0, 0)
) -> np.ndarray:
    """Replace black line pixels with an RGB color in a BGR OpenCV image."""
    if lineart.ndim != 2:
        raise ValueError("Line art must be a single-channel image.")
    if len(line_color) != 3 or any(not 0 <= channel <= 255 for channel in line_color):
        raise ValueError("Line color channels must be between 0 and 255.")
    colored = np.full((*lineart.shape, 3), 255, dtype=np.uint8)
    colored[lineart == 0] = tuple(reversed(line_color))
    return colored
