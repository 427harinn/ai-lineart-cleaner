#!/usr/bin/env python3
"""Extract simple black line art from an illustration image."""

import argparse
from pathlib import Path

import cv2
import numpy as np


DEFAULT_THRESHOLD = 180


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options for a single image conversion."""
    parser = argparse.ArgumentParser(
        description="Extract dark areas as black lines on a white PNG background."
    )
    parser.add_argument("input", type=Path, help="Input PNG or JPEG image")
    parser.add_argument("output", type=Path, help="Output PNG image")
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        choices=range(256),
        metavar="0-255",
        help=(
            "Brightness threshold from 0 to 255 "
            f"(default: {DEFAULT_THRESHOLD})"
        ),
    )
    return parser.parse_args()


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Return a grayscale image, compositing transparent pixels over white."""
    if image.ndim == 2:
        return image

    if image.ndim != 3:
        raise ValueError("Unsupported image format.")

    if image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if image.shape[2] == 4:
        # OpenCV loads PNG pixels as BGRA. Blend alpha against a white background.
        bgr = image[:, :, :3].astype(np.float32)
        alpha = image[:, :, 3:4].astype(np.float32) / 255.0
        white_background = np.full_like(bgr, 255.0)
        composited = bgr * alpha + white_background * (1.0 - alpha)
        return cv2.cvtColor(composited.astype(np.uint8), cv2.COLOR_BGR2GRAY)

    raise ValueError("Unsupported number of image channels.")


def extract_lineart(image: np.ndarray, threshold: int) -> np.ndarray:
    """Convert pixels at or below the threshold to black; all others to white."""
    grayscale = to_grayscale(image)
    _, lineart = cv2.threshold(grayscale, threshold, 255, cv2.THRESH_BINARY)
    return lineart


def main() -> int:
    args = parse_arguments()

    if args.output.suffix.lower() != ".png":
        print("Error: output file must have a .png extension.")
        return 2

    image = cv2.imread(str(args.input), cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"Error: could not read input image: {args.input}")
        return 1

    try:
        lineart = extract_lineart(image, args.threshold)
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), lineart):
        print(f"Error: could not write output image: {args.output}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
