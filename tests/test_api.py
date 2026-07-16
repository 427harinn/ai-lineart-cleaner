import cv2
import numpy as np
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


def test_extract_png_and_default_threshold():
    data = png_bytes(np.array([[80, 81]], dtype=np.uint8))
    response = client.post('/api/extract', files={'image': ('sample.png', data, 'image/png')})
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    assert 'sample-lineart.png' in response.headers['content-disposition']
    output = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_GRAYSCALE)
    assert np.array_equal(output, np.array([[0, 255]], dtype=np.uint8))


def test_extract_rejects_invalid_input():
    bad_threshold = client.post('/api/extract', data={'threshold': '256'}, files={'image': ('sample.png', png_bytes(np.zeros((1, 1), dtype=np.uint8)), 'image/png')})
    assert bad_threshold.status_code == 422
    invalid_image = client.post('/api/extract', files={'image': ('bad.png', b'not an image', 'image/png')})
    assert invalid_image.status_code == 400
