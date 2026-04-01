"""
data_loader.py — Loads the cleaned Parquet dataset once at startup and
exposes helper functions for the API routers.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Path resolution — works regardless of the working directory
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PARQUET_PATH = _REPO_ROOT / "clean_data" / "via_rail_clean.parquet"

# Module-level singleton: loaded once when the module is first imported.
_df: pd.DataFrame | None = None


def _load() -> pd.DataFrame:
    """Read the Parquet file and return the DataFrame."""
    if not _PARQUET_PATH.exists():
        # Return an empty DataFrame with the expected columns so the API can
        # still start when no dataset has been built yet.
        return pd.DataFrame(
            columns=[
                "scrape_date_est",
                "train_key",
                "train_number",
                "service_date",
                "origin",
                "destination",
                "departed",
                "arrived",
                "stop_sequence",
                "station_name",
                "station_code",
                "scheduled_arrival_utc",
                "estimated_arrival_utc",
                "scheduled_departure_utc",
                "estimated_departure_utc",
                "delay_minutes",
                "diff_status",
                "is_on_time",
                "is_late_15",
                "is_late_60",
                "is_corridor",
            ]
        )
    return pd.read_parquet(_PARQUET_PATH)


def get_df() -> pd.DataFrame:
    """Return the singleton DataFrame, loading it on first call."""
    global _df
    if _df is None:
        _df = _load()
    return _df


# ---------------------------------------------------------------------------
# Filtered-view helpers
# ---------------------------------------------------------------------------

def get_corridor_df() -> pd.DataFrame:
    """Return rows that belong to the Windsor–Québec City corridor."""
    df = get_df()
    if df.empty or "is_corridor" not in df.columns:
        return df
    return df[df["is_corridor"].fillna(False)]


def get_recent_df(days: int = 30) -> pd.DataFrame:
    """Return rows from the most recent *days* EST calendar days."""
    df = get_df()
    if df.empty or "scrape_date_est" not in df.columns:
        return df
    cutoff = df["scrape_date_est"].max() - pd.Timedelta(days=days - 1)
    return df[df["scrape_date_est"] >= cutoff]
