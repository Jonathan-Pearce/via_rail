"""
predict.py — Predicted arrival delay for a given train.

GET /api/predict/{train_key}
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.data_loader import get_df

router = APIRouter(tags=["predict"])


@router.get("/predict/{train_key}")
def get_prediction(train_key: str) -> dict[str, Any]:
    """
    Return a simple historical-average–based arrival delay prediction for the
    requested train key.

    When a trained ML model is available at ``models/arrival_model.joblib``
    this stub should be replaced with real inference.  Until then it returns
    the mean historical delay for the train (or a global mean as fallback).

    Response shape:
        {
            "train_key": "60",
            "predicted_delay_minutes": 8.2,
            "confidence": "low",
            "note": "historical average — no ML model loaded"
        }
    """
    df = get_df()

    if df.empty:
        return {
            "train_key": train_key,
            "predicted_delay_minutes": None,
            "confidence": "none",
            "note": "no data available",
        }

    train_df = df[df["train_key"] == train_key].dropna(subset=["delay_minutes"])

    if train_df.empty:
        # Try matching on train_number instead (e.g. "60" matches "60 (03-28)")
        train_number = train_key.split()[0]
        train_df = df[df["train_number"] == train_number].dropna(
            subset=["delay_minutes"]
        )

    if train_df.empty:
        raise HTTPException(
            status_code=404, detail=f"No historical data found for train '{train_key}'"
        )

    predicted = round(float(train_df["delay_minutes"].mean()), 2)

    return {
        "train_key": train_key,
        "predicted_delay_minutes": predicted,
        "confidence": "low",
        "note": "historical average — no ML model loaded",
    }
