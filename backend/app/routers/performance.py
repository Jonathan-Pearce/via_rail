"""
performance.py — Timeseries performance and aggregate summary endpoints.

GET /api/performance   — daily on-time / late counts (optionally filtered)
GET /api/summary       — aggregate stats for a rolling period
"""

from __future__ import annotations

from typing import Any, Literal, Optional

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


def _apply_common_filters(
    df: pd.DataFrame,
    *,
    period: str,
    corridor_only: bool,
    train_number: Optional[str],
    station_code: Optional[str],
    origin: Optional[str],
    destination: Optional[str],
) -> pd.DataFrame:
    """Apply the standard set of query-parameter filters to *df*."""
    df = _filter_by_period(df, period)

    if corridor_only:
        df = df[df["is_corridor"].fillna(False)]

    if train_number is not None:
        df = df[df["train_number"] == train_number]

    if station_code is not None:
        df = df[df["station_code"] == station_code.upper()]

    if origin is not None:
        df = df[df["origin"].str.upper() == origin.upper()]

    if destination is not None:
        df = df[df["destination"].str.upper() == destination.upper()]

    return df


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
    period: Literal["7d", "30d", "365d"] = Query("30d", description="Rolling window: 7d | 30d | 365d"),
    corridor_only: bool = Query(False, description="Restrict to corridor trains"),
    train_number: Optional[str] = Query(None, description="Filter to a specific train number"),
    station_code: Optional[str] = Query(None, description="Filter to stops at a specific station"),
    origin: Optional[str] = Query(None, description="Filter by origin city"),
    destination: Optional[str] = Query(None, description="Filter by destination city"),
) -> list[dict[str, Any]]:
    """
    Return a daily timeseries of on-time percentage and average delay.

    Each element:
        {
            "date": "2025-04-01",          # EST calendar date (ISO 8601)
            "on_time_pct": 72.4,           # percentage of stops <= 5 min late
            "avg_delay_minutes": 8.3,      # mean delay across all stops
            "late_15_pct": 18.2,           # percentage of stops >= 15 min late
            "late_60_pct": 3.1,            # percentage of stops >= 60 min late
            "total_stops": 142             # number of stop records that day
        }
    """
    df = get_df()

    if df.empty:
        return []

    df = _apply_common_filters(
        df,
        period=period,
        corridor_only=corridor_only,
        train_number=train_number,
        station_code=station_code,
        origin=origin,
        destination=destination,
    )

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
            on_time_pct=("is_on_time", "mean"),
            avg_delay_minutes=("delay_minutes", "mean"),
            late_15_pct=("is_late_15", "mean"),
            late_60_pct=("is_late_60", "mean"),
            total_stops=("delay_minutes", "count"),
        )
        .reset_index()
        .sort_values("scrape_date_est")
    )

    result = []
    for _, row in grouped.iterrows():
        result.append({
            "date": str(row["scrape_date_est"]),
            "on_time_pct": round(float(row["on_time_pct"]) * 100, 1),
            "avg_delay_minutes": round(float(row["avg_delay_minutes"]), 2),
            "late_15_pct": round(float(row["late_15_pct"]) * 100, 1),
            "late_60_pct": round(float(row["late_60_pct"]) * 100, 1),
            "total_stops": int(row["total_stops"]),
        })

    return result


# ---------------------------------------------------------------------------
# GET /api/summary
# ---------------------------------------------------------------------------

@router.get("/summary")
def get_summary(
    period: Literal["7d", "30d", "365d"] = Query("30d", description="Rolling window: 7d | 30d | 365d"),
    corridor_only: bool = Query(False, description="Restrict to corridor trains"),
    train_number: Optional[str] = Query(None, description="Filter to a specific train number"),
    station_code: Optional[str] = Query(None, description="Filter to stops at a specific station"),
    origin: Optional[str] = Query(None, description="Filter by origin city"),
    destination: Optional[str] = Query(None, description="Filter by destination city"),
) -> dict[str, Any]:
    """
    Return aggregate performance stats for the requested rolling period.

        {
            "period": "30d",
            "total_stops": 4200,
            "on_time_pct": 68.0,
            "late_15_pct": 21.0,
            "late_60_pct": 4.0,
            "avg_delay_minutes": 9.1
        }
    """
    df = get_df()

    if df.empty:
        return {
            "period": period,
            "total_stops": 0,
            "on_time_pct": None,
            "late_15_pct": None,
            "late_60_pct": None,
            "avg_delay_minutes": None,
        }

    df = _apply_common_filters(
        df,
        period=period,
        corridor_only=corridor_only,
        train_number=train_number,
        station_code=station_code,
        origin=origin,
        destination=destination,
    )

    df_delay = df.dropna(subset=["delay_minutes"])

    on_time_mean = _safe_mean(df_delay["is_on_time"].dropna())
    late_15_mean = _safe_mean(df_delay["is_late_15"].dropna())
    late_60_mean = _safe_mean(df_delay["is_late_60"].dropna())
    avg_delay_mean = _safe_mean(df_delay["delay_minutes"])

    return {
        "period": period,
        "total_stops": int(len(df_delay)),
        "on_time_pct": round(on_time_mean * 100, 1) if on_time_mean is not None else None,
        "late_15_pct": round(late_15_mean * 100, 1) if late_15_mean is not None else None,
        "late_60_pct": round(late_60_mean * 100, 1) if late_60_mean is not None else None,
        "avg_delay_minutes": round(avg_delay_mean, 2) if avg_delay_mean is not None else None,
    }
