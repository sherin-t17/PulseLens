"""
PulseLens backend entry point.
Run from the backend folder:   uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analyze, history, report
from app.database.db import init_db
from app.utils.errors import PulseLensError
from app.utils.paths import ensure_folders

logger = logging.getLogger("pulselens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_folders()   # uploads/ and reports/
    init_db()          # creates pulselens.db + tables on first run
    yield


app = FastAPI(title="PulseLens API", version="0.1.0", lifespan=lifespan)

# CORS lets the React site (a different port/device) call this API.
# "*" is fine for a local student prototype; restrict it if you ever deploy.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(PulseLensError)
async def handle_pulselens_error(request, exc: PulseLensError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def handle_unexpected_error(request, exc: Exception):
    logger.exception("Unexpected error")   # full details only in the server terminal
    return JSONResponse(status_code=500,
                        content={"detail": "Something went wrong on the server. Please try again."})


app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(report.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "PulseLens", "note": "Student prototype, not a medical device"}

@app.get("/")
def root():
    return {"app": "PulseLens API", "docs": "Open /docs to test the API"}