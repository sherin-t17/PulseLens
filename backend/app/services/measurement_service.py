"""Database operations for measurements (save, list, get, delete, statistics)."""

import json
import math

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.measurement import Measurement
from app.utils.errors import PulseLensError


def build_payload(result):
    """
    Turn the big numpy arrays from the analysis into small JSON-friendly lists.
    We downsample so each row in the database stays small.
    """
    t, y = result["time_axis"], result["filtered_signal"]
    step = max(1, math.ceil(len(y) / 900))
    ppg = {
        "t": [round(float(v), 3) for v in t[::step]],
        "y": [round(float(v), 4) for v in y[::step]],
    }

    freqs, power = result["freqs"], result["power"]
    mask = (freqs >= 0.5) & (freqs <= 4.5)          # only the interesting part
    f, p = freqs[mask], power[mask]
    if p.max() > 0:
        p = p / p.max()                             # strongest peak = 1.0
    step = max(1, math.ceil(len(f) / 600))
    spectrum = {
        "f": [round(float(v), 4) for v in f[::step]],
        "p": [round(float(v), 4) for v in p[::step]],
    }
    return ppg, spectrum


def save_measurement(db: Session, client_id, user_name, result):
    ppg, spectrum = build_payload(result)
    row = Measurement(
        client_id=client_id,
        user_name=user_name,
        bpm=result["bpm"],
        quality_label=result["quality_label"],
        quality_score=result["quality_score"],
        duration_seconds=result["duration_seconds"],
        dominant_frequency_hz=result["dominant_frequency_hz"],
        interpretation=result["interpretation"],
        channel=result.get("channel", "green"),
        ppg_json=json.dumps(ppg),
        spectrum_json=json.dumps(spectrum),
    )
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except SQLAlchemyError:
        db.rollback()
        raise PulseLensError("The measurement could not be saved. Please try again.", 500)
    return row


def list_measurements(db: Session, client_id):
    """All measurements of this client, newest first."""
    try:
        return (
            db.query(Measurement)
            .filter(Measurement.client_id == client_id)
            .order_by(Measurement.created_at.desc())
            .all()
        )
    except SQLAlchemyError:
        raise PulseLensError("The history could not be loaded.", 500)


def get_measurement(db: Session, client_id, measurement_id):
    row = (
        db.query(Measurement)
        .filter(Measurement.id == measurement_id, Measurement.client_id == client_id)
        .first()
    )
    if row is None:
        raise PulseLensError("Measurement not found.", 404)
    return row


def delete_measurement(db: Session, client_id, measurement_id):
    row = get_measurement(db, client_id, measurement_id)
    try:
        db.delete(row)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise PulseLensError("The measurement could not be deleted.", 500)


def delete_all(db: Session, client_id):
    try:
        count = db.query(Measurement).filter(Measurement.client_id == client_id).delete()
        db.commit()
        return count
    except SQLAlchemyError:
        db.rollback()
        raise PulseLensError("The history could not be deleted.", 500)


def compute_stats(measurements):
    """Simple numbers for the History page. No medical conclusions."""
    if not measurements:
        return {"count": 0, "latest": None, "average": None, "minimum": None, "maximum": None}
    bpms = [m.bpm for m in measurements]
    return {
        "count": len(bpms),
        "latest": bpms[0],                      # list is newest-first
        "average": round(sum(bpms) / len(bpms), 1),
        "minimum": min(bpms),
        "maximum": max(bpms),
    }