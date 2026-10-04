"""Central place for folder and file locations."""

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]   # .../PulseLens/backend
PROJECT_DIR = BACKEND_DIR.parent                     # .../PulseLens
UPLOAD_DIR = PROJECT_DIR / "uploads"
REPORT_DIR = PROJECT_DIR / "reports"
DB_PATH = BACKEND_DIR / "pulselens.db"


def ensure_folders():
    UPLOAD_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)