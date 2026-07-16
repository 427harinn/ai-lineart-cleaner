#!/usr/bin/env python3
"""Command-line interface for extracting simple black line art."""

import argparse
from pathlib import Path

import cv2

from app.lineart import (
    DEFAULT_LINE_COLOR,
    DEFAULT_THRESHOLD,
    colorize_lineart,
    extract_lineart,
    parse_line_color,
)


def line_color_argument(value: str) -> str:
    """Validate a command-line line color while retaining its HEX representation."""
    try:
        parse_line_color(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error
    return value


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
    parser.add_argument(
        "--thin-line-assist",
        action="store_true",
        help="Use weak local contrast enhancement before thresholding.",
    )
    parser.add_argument(
        "--repair-strength",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Repair tiny line gaps: 0=off, 1=weak, 2=stronger (default: 0)",
    )
    parser.add_argument(
        "--line-color",
        type=line_color_argument,
        default=DEFAULT_LINE_COLOR,
        metavar="#RRGGBB",
        help="Line color in #RRGGBB format (default: #000000)",
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
        lineart = extract_lineart(
            image,
            args.threshold,
            thin_line_assist=args.thin_line_assist,
            repair_strength=args.repair_strength,
        )
        colored_lineart = colorize_lineart(lineart, parse_line_color(args.line_color))
    except ValueError as error:
        print(f"Error: {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), colored_lineart):
        print(f"Error: could not write output image: {args.output}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
