#!/usr/bin/env python3
"""Command-line interface for extracting simple black line art."""

import argparse
from pathlib import Path

import cv2

from app.lineart import DEFAULT_THRESHOLD, extract_lineart


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options for one image conversion."""
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
        help=f"Brightness threshold from 0 to 255 (default: {DEFAULT_THRESHOLD})",
    )
    return parser.parse_args()


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
