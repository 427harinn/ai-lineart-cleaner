import subprocess
import sys

import cv2
import numpy as np


def test_cli_applies_line_color(tmp_path):
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    assert cv2.imwrite(str(input_path), np.array([[80, 81]], dtype=np.uint8))

    result = subprocess.run(
        [sys.executable, "extract_lineart.py", str(input_path), str(output_path), "--line-color", "#336699"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    output = cv2.imread(str(output_path), cv2.IMREAD_COLOR)
    assert np.array_equal(output, np.array([[[153, 102, 51], [255, 255, 255]]], dtype=np.uint8))


def test_cli_rejects_invalid_line_color(tmp_path):
    result = subprocess.run(
        [sys.executable, "extract_lineart.py", "input.png", str(tmp_path / "output.png"), "--line-color", "red"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "#RRGGBB" in result.stderr
