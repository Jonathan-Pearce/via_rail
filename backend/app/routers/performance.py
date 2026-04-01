"""
performance.py — Timeseries performance and aggregate summary endpoints.

GET /api/performance   — daily on-time / late counts (optionally filtered)
GET /api/summary       — aggregate stats for a rolling period
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, Query

from app.data_loader import get_df

router = APIRouter(tags=["performance"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PERIOD_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "365d": 365}


def _filter_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """Return rows within the rolling *period* window."""
    if df.empty or "scrape_date_est" not in df.columns:
        return df
    days = _PERIOD_DAYS.get(period, 30)
    cutoff = df["scrape_date_est"].max() - pd.Timedelta(days=days - 1)
    return df[df["scrape_date_est"] >= cutoff]


def _safe_mean(series: pd.Series) -> float | None:
    """Return the mean of a boolean/numeric series, or None if empty."""
    if series.empty:
        return None
    return float(series.mean())


# ---------------------------------------------------------------------------
# GET /api/performance
# ---------------------------------------------------------------------------

@router.get("/performance")
def get_performance(
    corridor_only: bool = Query(False, description="Restrict to corridor trains"),
    period: str = Query("30d", description="Rolling window: 7d | 30d | 365d"),
) -> list[dict[str, Any]]:
    """
    Return a daily timeseries of on-time rate and average delay.

    Each element:
        {
            "date": "2025-04-01",          # EST calendar date (ISO 8601)
            "on_time_rate": 0.72,          # fraction of stops <= 5 min late
            "avg_delay_minutes": 8.3,      # mean delay across all stops
            "total_stops": 142             # number of stop records that day
        }
    """
    df = get_df()

    if df.empty:
        return []

    df = _filter_by_period(df, period)

    if corridor_only:
        df = df[df["is_corridor"].fillna(False)]

    if df.empty:
        return []

    # Work only with rows that have delay data
    df_delay = df.dropna(subset=["delay_minutes", "is_on_time"])

    if df_delay.empty:
        return []

    grouped = (
        df_delay
        .groupby("scrape_date_est")
        .agg(
            on_time_rate=("is_on_time", "mean"),
            avg_delay_minutes=("delay_minutes", "mean"),
            total_stops=("delay_minutes", "count"),
        )
        .reset_index()
        .sort_values("scrape_date_est")
    )

    result = []
    for _, row in grouped.iterrows():
        result.append({
            "date": str(row["scrape_date_est"]),
            "on_time_rate": round(float(row["on_time_rate"]), 4),
            "avg_delay_minutes": round(float(row["avg_delay_minutes"]), 2),
            "total_stops": int(row["total_stops"]),
        })

    return result


# ---------------------------------------------------------------------------
# GET /api/summary
# ---------------------------------------------------------------------------

@router.get("/summary")
def get_summary(
    period: str = Query("30d", description="Rolling window: 7d | 30d | 365d"),
    corridor_only: bool = Query(False, description="Restrict to corridor trains"),
) -> dict[str, Any]:
    """
    Return aggregate performance stats for the requested rolling period.

        {
            "period": "30d",
            "total_stops": 4200,
            "on_time_rate": 0.68,
            "late_15_rate": 0.21,
            "late_60_rate": 0.04,
            "avg_delay_minutes": 9.1
        }
    """
    df = get_df()

    if df.empty:
        return {
            "period": period,
            "total_stops": 0,
            "on_time_rate": None,
            "late_15_rate": None,
            "late_60_rate": None,
            "avg_delay_minutes": None,
        }

    df = _filter_by_period(df, period)

    if corridor_only:
        df = df[df["is_corridor"].fillna(False)]

    df_delay = df.dropna(subset=["delay_minutes"])

    return {
        "period": period,
        "total_stops": int(len(df_delay)),
        "on_time_rate": _safe_mean(df_delay["is_on_time"].dropna()),
        "late_15_rate": _safe_mean(df_delay["is_late_15"].dropna()),
        "late_60_rate": _safe_mean(df_delay["is_late_60"].dropna()),
        "avg_delay_minutes": _safe_mean(df_delay["delay_minutes"]),
    }
