"""
main.py — FastAPI application entry-point.

Start with:
    cd backend && uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import live, performance, predict, stations

app = FastAPI(title="Via Rail Performance API", version="0.1.0")

# ---------------------------------------------------------------------------
# CORS — allow the Vite dev server and any future production origin
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(performance.router, prefix="/api")
app.include_router(stations.router, prefix="/api")
app.include_router(live.router, prefix="/api")
app.include_router(predict.router, prefix="/api")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
