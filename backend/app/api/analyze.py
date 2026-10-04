"""POST /api/analyze : upload a video, get the BPM and graphs data back."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_client_id
from app.database.db import get_db
from app.processing.heart_rate import analyze_video
from app.services.measurement_service import save_measurement
from app.utils.errors import PulseLensError
from app.utils.paths import UPLOAD_DIR, ensure_folders

router = APIRouter(prefix="/api", tags=["analysis"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}   # .mov = iPhone videos
MAX_MB = 100


@router.post("/analyze", status_code=201)
def analyze(
    file: UploadFile = File(...),
    name: str = Form(""),
    channel: str = Form("green"),
    client_id: str = Depends(get_client_id),
    db: Session = Depends(get_db),
):
    if not file or not file.filename:
        raise PulseLensError("No video selected. Please choose a video file.", 400)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise PulseLensError("Unsupported file type. Please upload an MP4, AVI or MOV video.", 400)

    if channel not in ("green", "red"):
        channel = "green"
    user_name = name.strip()[:60] or "Anonymous User"

    ensure_folders()
    temp_path = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    try:
        # Save the upload in 1 MB chunks so big files do not fill the memory
        size = 0
        with open(temp_path, "wb") as out:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_MB * 1024 * 1024:
                    raise PulseLensError(f"The video is larger than {MAX_MB} MB. "
                                         "Please record at 720p or a shorter clip.", 413)
                out.write(chunk)
        if size == 0:
            raise PulseLensError("The uploaded file is empty.", 400)

        result = analyze_video(temp_path, channel=channel)
    finally:
        temp_path.unlink(missing_ok=True)   # the video is deleted after processing

    result["channel"] = channel
    if result["bpm"] is None:               # poor signal: do NOT save or show a BPM
        raise PulseLensError(result["message"], 422)

    row = save_measurement(db, client_id, user_name, result)
    return row.to_dict(detail=True)