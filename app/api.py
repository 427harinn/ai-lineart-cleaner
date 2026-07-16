"""FastAPI web interface for line art extraction."""

from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.lineart import DEFAULT_THRESHOLD, extract_lineart

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


@app.post("/api/extract")
async def extract(
    image: UploadFile | None = File(default=None),
    threshold: int = Form(default=DEFAULT_THRESHOLD),
) -> Response:
    """Decode a PNG/JPEG upload and return its line-art PNG without persisting it."""
    if image is None or not image.filename:
        raise HTTPException(status_code=400, detail="An image file is required.")
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PNG and JPEG images are supported.")
    if not 0 <= threshold <= 255:
        raise HTTPException(status_code=422, detail="Threshold must be between 0 and 255.")
    data = await image.read()
    decoded = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if decoded is None:
        raise HTTPException(status_code=400, detail="The uploaded file could not be decoded as an image.")
    try:
        lineart = extract_lineart(decoded, threshold)
        success, encoded = cv2.imencode(".png", lineart)
    except (ValueError, cv2.error) as error:
        raise HTTPException(status_code=400, detail=f"Could not process image: {error}") from error
    if not success:
        raise HTTPException(status_code=500, detail="Could not encode result as PNG.")
    stem = Path(image.filename).stem or "lineart"
    return Response(
        content=encoded.tobytes(),
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{stem}-lineart.png"'},
    )
