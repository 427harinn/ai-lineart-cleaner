import numpy as np

from app.lineart import DEFAULT_THRESHOLD, extract_lineart


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
