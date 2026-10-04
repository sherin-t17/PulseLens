"""The 'measurements' table: one row per successful analysis."""

import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database.db import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True, nullable=False)   # anonymous browser id
    user_name = Column(String, default="Anonymous User")
    created_at = Column(DateTime, default=datetime.now)
    bpm = Column(Float, nullable=False)
    quality_label = Column(String, nullable=False)           # GOOD / MEDIUM / POOR
    quality_score = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    dominant_frequency_hz = Column(Float, nullable=False)
    interpretation = Column(String)
    channel = Column(String, default="green")
    ppg_json = Column(Text)        # downsampled PPG signal, stored as JSON text
    spectrum_json = Column(Text)   # downsampled FFT spectrum, stored as JSON text

    def to_dict(self, detail=False):
        data = {
            "id": self.id,
            "user_name": self.user_name,
            "date": self.created_at.strftime("%d %b %Y"),
            "time": self.created_at.strftime("%I:%M %p"),
            "created_at": self.created_at.isoformat(),
            "bpm": self.bpm,
            "quality_label": self.quality_label,
            "quality_score": self.quality_score,
            "duration_seconds": self.duration_seconds,
            "dominant_frequency_hz": self.dominant_frequency_hz,
            "interpretation": self.interpretation,
            "channel": self.channel,
        }
        if detail:  # the graphs' data (only for the single-measurement view)
            data["ppg"] = json.loads(self.ppg_json)
            data["spectrum"] = json.loads(self.spectrum_json)
        return data