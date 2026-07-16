import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def png_bytes(image: np.ndarray) -> bytes:
    ok, encoded = cv2.imencode('.png', image)
    assert ok
    return encoded.tobytes()


def test_health_and_index():
    assert client.get('/api/health').json() == {'status': 'ok'}
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']


def test_extract_png_and_default_threshold_uses_black_lines():
    data = png_bytes(np.array([[80, 81]], dtype=np.uint8))
    response = client.post('/api/extract', files={'image': ('sample.png', data, 'image/png')})
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    assert 'sample-lineart.png' in response.headers['content-disposition']
    output = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
    assert np.array_equal(output, np.array([[[0, 0, 0], [255, 255, 255]]], dtype=np.uint8))


def test_extract_applies_requested_line_color():
    data = png_bytes(np.array([[80, 81]], dtype=np.uint8))
    response = client.post(
        '/api/extract', data={'line_color': '#FF0000'},
        files={'image': ('sample.png', data, 'image/png')},
    )
    assert response.status_code == 200
    output = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)
    assert output is not None
    assert np.array_equal(output, np.array([[[0, 0, 255], [255, 255, 255]]], dtype=np.uint8))


def test_extract_accepts_enhancement_options_together_with_line_color():
    image = np.full((128, 128), 180, dtype=np.uint8)
    image[:, 60:63] = 100
    data = png_bytes(image)
    for form_data in (
        {'thin_line_assist': 'true'},
        {'repair_strength': '1'},
        {'thin_line_assist': 'true', 'repair_strength': '1', 'line_color': '#336699'},
    ):
        response = client.post(
            '/api/extract', data=form_data,
            files={'image': ('説明画像.png', data, 'image/png')},
        )
        assert response.status_code == 200
        assert cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR) is not None


def test_extract_rejects_invalid_input():
    bad_threshold = client.post('/api/extract', data={'threshold': '256'}, files={'image': ('sample.png', png_bytes(np.zeros((1, 1), dtype=np.uint8)), 'image/png')})
    assert bad_threshold.status_code == 422
    bad_color = client.post('/api/extract', data={'line_color': '#fff'}, files={'image': ('sample.png', png_bytes(np.zeros((1, 1), dtype=np.uint8)), 'image/png')})
    assert bad_color.status_code == 422
    invalid_image = client.post('/api/extract', files={'image': ('bad.png', b'not an image', 'image/png')})
    assert invalid_image.status_code == 400


@pytest.mark.parametrize('repair_strength', ['-1', '3'])
def test_extract_rejects_invalid_repair_strength(repair_strength):
    response = client.post(
        '/api/extract', data={'repair_strength': repair_strength},
        files={'image': ('sample.png', png_bytes(np.zeros((1, 1), dtype=np.uint8)), 'image/png')},
    )
    assert response.status_code == 422


def test_extract_supports_unicode_and_unsafe_filenames():
    data = png_bytes(np.array([[20]], dtype=np.uint8))
    response = client.post(
        '/api/extract',
        files={'image': ('説明画像.png', data, 'image/png')},
    )
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    disposition = response.headers['content-disposition']
    assert 'filename="lineart.png"' in disposition
    assert "filename*=UTF-8''%E8%AA%AC%E6%98%8E%E7%94%BB%E5%83%8F-lineart.png" in disposition
    output = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_GRAYSCALE)
    assert output is not None

    response = client.post(
        '/api/extract',
        files={'image': ('../line art!?.jpg', data, 'image/jpeg')},
    )
    assert response.status_code == 200
    assert 'filename="lineart-lineart.png"' in response.headers['content-disposition']
    assert 'filename*=UTF-8\'\'line%20art%21-lineart.png' in response.headers['content-disposition']
