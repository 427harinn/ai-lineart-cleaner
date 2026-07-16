import numpy as np

import pytest

from app.lineart import (
    DEFAULT_LINE_COLOR,
    DEFAULT_THRESHOLD,
    colorize_lineart,
    extract_lineart,
    parse_line_color,
)


def test_threshold_and_default_are_80():
    image = np.array([[80, 81]], dtype=np.uint8)
    assert DEFAULT_THRESHOLD == 80
    assert np.array_equal(extract_lineart(image), np.array([[0, 255]], dtype=np.uint8))


def test_grayscale_bgr_and_bgra_images_are_supported():
    gray = np.array([[10, 200]], dtype=np.uint8)
    bgr = np.dstack((gray, gray, gray))
    transparent_bgra = np.array([[[0, 0, 0, 0], [0, 0, 0, 255]]], dtype=np.uint8)
    for image in (gray, bgr):
        result = extract_lineart(image, 80)
        assert result.dtype == np.uint8 and result.ndim == 2
        assert np.array_equal(result, np.array([[0, 255]], dtype=np.uint8))
    assert np.array_equal(extract_lineart(transparent_bgra, 80), np.array([[255, 0]], dtype=np.uint8))


def test_colorize_lineart_uses_bgr_for_opencv_and_keeps_background_white():
    lineart = np.array([[0, 255]], dtype=np.uint8)
    result = colorize_lineart(lineart, parse_line_color("#FF0000"))
    assert result.dtype == np.uint8
    assert result.shape == (1, 2, 3)
    assert np.array_equal(result[0, 0], np.array([0, 0, 255], dtype=np.uint8))
    assert np.array_equal(result[0, 1], np.array([255, 255, 255], dtype=np.uint8))


def test_default_line_color_is_black():
    assert DEFAULT_LINE_COLOR == "#000000"
    assert np.array_equal(colorize_lineart(np.array([[0]], dtype=np.uint8)), np.zeros((1, 1, 3), dtype=np.uint8))


@pytest.mark.parametrize("value", ["#000000", "#ffffff", "#5A3A32"])
def test_parse_line_color_accepts_six_digit_hex(value):
    assert len(parse_line_color(value)) == 3


@pytest.mark.parametrize("value", ["#fff", "000000", "red", "#GG0000", ""])
def test_parse_line_color_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="#RRGGBB"):
        parse_line_color(value)
