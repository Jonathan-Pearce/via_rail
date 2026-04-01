"""
stations.py — Station list with average delay statistics.

GET /api/stations
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.data_loader import get_df

router = APIRouter(tags=["stations"])


@router.get("/stations")
def get_stations(
    corridor_only: bool = Query(False, description="Restrict to corridor stations"),
) -> list[dict[str, Any]]:
    """
    Return a list of stations with aggregate delay statistics.

    Each element:
        {
            "station_code": "MTRL",
            "station_name": "Montréal",
            "is_corridor": true,
            "avg_delay_minutes": 12.4,
            "on_time_pct": 61.0,
            "total_stops": 320
        }
    """
    df = get_df()

    if df.empty:
        return []

    if corridor_only:
        df = df[df["is_corridor"].fillna(False)]

    if df.empty:
        return []

    df_delay = df.dropna(subset=["delay_minutes"])

    if df_delay.empty:
        return []

    grouped = (
        df_delay
        .groupby(["station_code", "station_name", "is_corridor"])
        .agg(
            avg_delay_minutes=("delay_minutes", "mean"),
            on_time_rate=("is_on_time", "mean"),
            total_stops=("delay_minutes", "count"),
        )
        .reset_index()
        .sort_values("station_name")
    )

    result = []
    for _, row in grouped.iterrows():
        result.append({
            "station_code": str(row["station_code"]),
            "station_name": str(row["station_name"]),
            "is_corridor": bool(row["is_corridor"]),
            "avg_delay_minutes": round(float(row["avg_delay_minutes"]), 2),
            "on_time_pct": round(float(row["on_time_rate"]) * 100, 1),
            "total_stops": int(row["total_stops"]),
        })

    return result
