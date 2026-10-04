"""History endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_client_id
from app.database.db import get_db
from app.services import measurement_service as svc

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
def list_history(client_id: str = Depends(get_client_id), db: Session = Depends(get_db)):
    items = svc.list_measurements(db, client_id)
    return {"stats": svc.compute_stats(items), "items": [m.to_dict() for m in items]}


@router.get("/{measurement_id}")
def get_one(measurement_id: int, client_id: str = Depends(get_client_id),
            db: Session = Depends(get_db)):
    return svc.get_measurement(db, client_id, measurement_id).to_dict(detail=True)


@router.delete("/{measurement_id}")
def delete_one(measurement_id: int, client_id: str = Depends(get_client_id),
               db: Session = Depends(get_db)):
    svc.delete_measurement(db, client_id, measurement_id)
    return {"deleted": measurement_id}


@router.delete("")
def delete_everything(client_id: str = Depends(get_client_id), db: Session = Depends(get_db)):
    return {"deleted_count": svc.delete_all(db, client_id)}