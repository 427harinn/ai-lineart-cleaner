"""Reusable image processing for black-line-on-white line art."""

import cv2
import numpy as np

DEFAULT_THRESHOLD = 80


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
