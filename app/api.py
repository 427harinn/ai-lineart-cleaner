"""FastAPI web interface for line art extraction."""

from pathlib import Path
import re
from urllib.parse import quote

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.lineart import (
    DEFAULT_LINE_COLOR,
    DEFAULT_THRESHOLD,
    colorize_lineart,
    extract_lineart,
    parse_line_color,
)

app = FastAPI(title="AI Lineart Cleaner")
STATIC_DIR = Path(__file__).parent / "static"
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg"}
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    """Serve the single-page browser UI."""
    return FileResponse(STATIC_DIR / "index.html", media_type="text/html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def download_filename(filename: str) -> tuple[str, str]:
    """Return an ASCII fallback and RFC 5987 UTF-8 filename for a PNG download."""
    base_name = Path(filename.replace("\\", "/")).name
    stem = re.sub(r"[\x00-\x1f\x7f]", "", Path(base_name).stem).strip(" .")
    output_name = f"{stem or 'lineart'}-lineart.png"
    ascii_stem = re.sub(r"[^A-Za-z0-9_-]", "", stem).strip("._-")
    fallback_name = f"{ascii_stem}-lineart.png" if ascii_stem else "lineart.png"
    return fallback_name, quote(output_name, safe="")


@app.post("/api/extract")
async def extract(
    image: UploadFile | None = File(default=None),
    threshold: int = Form(default=DEFAULT_THRESHOLD),
    line_color: str = Form(default=DEFAULT_LINE_COLOR),
    thin_line_assist: bool = Form(default=False),
    repair_strength: int = Form(default=0, ge=0, le=2),
) -> Response:
    """Decode a PNG/JPEG upload and return its line-art PNG without persisting it."""
    if image is None or not image.filename:
        raise HTTPException(status_code=400, detail="An image file is required.")
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PNG and JPEG images are supported.")
    if not 0 <= threshold <= 255:
        raise HTTPException(status_code=422, detail="Threshold must be between 0 and 255.")
    try:
        rgb_line_color = parse_line_color(line_color)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    data = await image.read()
    decoded = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if decoded is None:
        raise HTTPException(status_code=400, detail="The uploaded file could not be decoded as an image.")
    try:
        lineart = extract_lineart(
            decoded,
            threshold,
            thin_line_assist=thin_line_assist,
            repair_strength=repair_strength,
        )
        colored_lineart = colorize_lineart(lineart, rgb_line_color)
        success, encoded = cv2.imencode(".png", colored_lineart)
    except (ValueError, cv2.error) as error:
        raise HTTPException(status_code=400, detail=f"Could not process image: {error}") from error
    if not success:
        raise HTTPException(status_code=500, detail="Could not encode result as PNG.")
    fallback_name, encoded_name = download_filename(image.filename)
    content_disposition = (
        f'attachment; filename="{fallback_name}"; '
        f"filename*=UTF-8''{encoded_name}"
    )
    return Response(
        content=encoded.tobytes(),
        media_type="image/png",
        headers={"Content-Disposition": content_disposition},
    )
