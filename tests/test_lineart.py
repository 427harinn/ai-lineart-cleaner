import numpy as np

import pytest

from app.lineart import (
    DEFAULT_LINE_COLOR,
    DEFAULT_THRESHOLD,
    colorize_lineart,
    enhance_thin_lines,
    extract_lineart,
    parse_line_color,
    repair_lineart,
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


def test_thin_line_assist_is_optional_binary_and_does_not_mutate_input():
    image = np.full((128, 128), 180, dtype=np.uint8)
    image[:, 60:63] = 100
    original = image.copy()

    normal = extract_lineart(image, 80)
    assisted = extract_lineart(image, 80, thin_line_assist=True)

    assert np.array_equal(normal, np.full_like(image, 255))
    assert np.count_nonzero(assisted[:, 60:63] == 0) > 0
    assert assisted.dtype == np.uint8
    assert set(np.unique(assisted)).issubset({0, 255})
    assert np.array_equal(image, original)


def test_enhance_thin_lines_does_not_mutate_grayscale_input():
    grayscale = np.full((128, 128), 180, dtype=np.uint8)
    grayscale[:, 60:63] = 100
    original = grayscale.copy()
    enhanced = enhance_thin_lines(grayscale)
    assert enhanced.dtype == np.uint8
    assert np.array_equal(grayscale, original)


def test_repair_lineart_repairs_small_gaps_without_mutating_input():
    lineart = np.full((9, 9), 255, dtype=np.uint8)
    lineart[4, 2:7] = 0
    lineart[4, 4] = 255
    original = lineart.copy()

    no_repair = repair_lineart(lineart, 0)
    weak = repair_lineart(lineart, 1)
    stronger = repair_lineart(lineart, 2)

    assert np.array_equal(no_repair, lineart)
    assert weak[4, 4] == 0
    assert np.count_nonzero(stronger == 0) >= np.count_nonzero(weak == 0)
    assert np.any(weak == 255)
    assert weak.dtype == np.uint8
    assert set(np.unique(weak)).issubset({0, 255})
    assert np.array_equal(lineart, original)


@pytest.mark.parametrize("strength", [-1, 3])
def test_repair_lineart_rejects_invalid_strength(strength):
    with pytest.raises(ValueError, match="0, 1, or 2"):
        repair_lineart(np.full((3, 3), 255, dtype=np.uint8), strength)


@pytest.mark.parametrize("value", ["#000000", "#ffffff", "#5A3A32"])
def test_parse_line_color_accepts_six_digit_hex(value):
    assert len(parse_line_color(value)) == 3


@pytest.mark.parametrize("value", ["#fff", "000000", "red", "#GG0000", ""])
def test_parse_line_color_rejects_invalid_values(value):
    with pytest.raises(ValueError, match="#RRGGBB"):
        parse_line_color(value)
