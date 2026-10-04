"""GET /api/report : download the PDF report."""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_client_id
from app.database.db import get_db
from app.services.measurement_service import list_measurements
from app.services.report_service import build_report
from app.utils.errors import PulseLensError

router = APIRouter(prefix="/api", tags=["report"])


@router.get("/report")
def download_report(name: str = "", client_id: str = Depends(get_client_id),
                    db: Session = Depends(get_db)):
    items = list_measurements(db, client_id)
    if not items:
        raise PulseLensError("No measurements yet. Analyze a video first.", 404)
    user_name = name.strip()[:60] or items[0].user_name or "Anonymous User"
    path = build_report(items, user_name, client_id)
    return FileResponse(path, media_type="application/pdf", filename="PulseLens_Report.pdf")