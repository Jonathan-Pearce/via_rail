"""
build_historical.py — Process all raw JSON snapshots in raw_data/ into a
master Parquet dataset at clean_data/via_rail_clean.parquet.

File-selection rule:
    Scrapes run at ~03:00–04:30 UTC (~22:00–00:30 EST).  For each EST
    calendar day we keep only the *latest* scrape file whose UTC timestamp
    converts to that EST date.  This captures the final state of every
    train for that operating day.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "raw_data"
OUTPUT_PATH = Path(__file__).resolve().parent / "via_rail_clean.parquet"

# ---------------------------------------------------------------------------
# Timezone helpers
# ---------------------------------------------------------------------------
UTC = timezone.utc
EST = timezone(timedelta(hours=-5))

# ---------------------------------------------------------------------------
# Windsor–Québec corridor station codes
# ---------------------------------------------------------------------------
CORRIDOR_STATION_CODES: set[str] = {
    "WDON", "CHAT", "GLNC", "LNDN", "INGR", "WDST", "BRTF", "ALDR",
    "OAKV", "TRTO", "GUIL", "OSHA", "CBRG", "PHOP", "TRNJ", "BLVL",
    "NAPN", "KGON", "GANA", "BRKV", "CWLL", "ALEX", "CSLM", "OTTW",
    "FALL", "SMTF", "SLAM", "MTRL", "DORV", "COTO", "SHYA", "DRMV",
    "SFOY", "QBEC", "CHNY",
}

# ---------------------------------------------------------------------------
# Filename parsing
# ---------------------------------------------------------------------------
_FILENAME_RE = re.compile(
    r"Via_data_(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
)


def parse_utc_timestamp(filename: str) -> datetime | None:
    """Return the UTC datetime encoded in a raw-data filename, or None."""
    m = _FILENAME_RE.search(filename)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)


# ---------------------------------------------------------------------------
# File selection: one file per EST calendar day (latest UTC timestamp)
# ---------------------------------------------------------------------------
def select_files(raw_dir: Path) -> dict[date, Path]:
    """
    Return a mapping of {est_date: path_to_latest_file_for_that_day}.
    """
    best: dict[date, tuple[datetime, Path]] = {}

    for path in sorted(raw_dir.glob("Via_data_*.json")):
        ts_utc = parse_utc_timestamp(path.name)
        if ts_utc is None:
            continue
        est_date = ts_utc.astimezone(EST).date()
        if est_date not in best or ts_utc > best[est_date][0]:
            best[est_date] = (ts_utc, path)

    return {d: info[1] for d, info in best.items()}


# ---------------------------------------------------------------------------
# Datetime helpers
# ---------------------------------------------------------------------------
def _parse_dt(value: str | None) -> datetime | None:
    """Parse an ISO-8601 UTC string to an aware datetime, or None."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(UTC)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Flattening a single JSON file
# ---------------------------------------------------------------------------
def flatten_file(path: Path, scrape_date_est: date) -> list[dict]:
    """Return a list of row dicts for one raw JSON snapshot."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    rows: list[dict] = []

    for train_key, train in data.items():
        # Numeric part of the key (e.g. "2 (03-28)" → "2", "60" → "60")
        train_number = train_key.split()[0]

        # Service date from the "instance" field
        try:
            service_date = date.fromisoformat(train.get("instance", ""))
        except ValueError:
            service_date = None

        origin = train.get("from", "")
        destination = train.get("to", "")
        departed = bool(train.get("departed", False))
        arrived = bool(train.get("arrived", False))

        for seq, stop in enumerate(train.get("times", [])):
            delay_minutes = stop.get("diffMin")
            if delay_minutes is None:
                delay_minutes_int = None
                is_on_time = None
                is_late_15 = None
                is_late_60 = None
            else:
                delay_minutes_int = int(delay_minutes)
                is_on_time = delay_minutes_int <= 5
                is_late_15 = delay_minutes_int >= 15
                is_late_60 = delay_minutes_int >= 60

            arrival = stop.get("arrival") or {}
            departure = stop.get("departure") or {}
            station_code = stop.get("code", "")

            rows.append({
                "scrape_date_est": scrape_date_est,
                "train_key": train_key,
                "train_number": train_number,
                "service_date": service_date,
                "origin": origin,
                "destination": destination,
                "departed": departed,
                "arrived": arrived,
                "stop_sequence": seq,
                "station_name": stop.get("station", ""),
                "station_code": station_code,
                "scheduled_arrival_utc": _parse_dt(arrival.get("scheduled")),
                "estimated_arrival_utc": _parse_dt(arrival.get("estimated")),
                "scheduled_departure_utc": _parse_dt(departure.get("scheduled")),
                "estimated_departure_utc": _parse_dt(departure.get("estimated")),
                "delay_minutes": delay_minutes_int,
                "diff_status": stop.get("diff"),
                "is_on_time": is_on_time,
                "is_late_15": is_late_15,
                "is_late_60": is_late_60,
                "is_corridor": station_code in CORRIDOR_STATION_CODES,
            })

    return rows


# ---------------------------------------------------------------------------
# PyArrow schema — keeps dtypes deterministic even for empty files
# ---------------------------------------------------------------------------
SCHEMA = pa.schema([
    pa.field("scrape_date_est", pa.date32()),
    pa.field("train_key", pa.string()),
    pa.field("train_number", pa.string()),
    pa.field("service_date", pa.date32()),
    pa.field("origin", pa.string()),
    pa.field("destination", pa.string()),
    pa.field("departed", pa.bool_()),
    pa.field("arrived", pa.bool_()),
    pa.field("stop_sequence", pa.int32()),
    pa.field("station_name", pa.string()),
    pa.field("station_code", pa.string()),
    pa.field("scheduled_arrival_utc", pa.timestamp("us", tz="UTC")),
    pa.field("estimated_arrival_utc", pa.timestamp("us", tz="UTC")),
    pa.field("scheduled_departure_utc", pa.timestamp("us", tz="UTC")),
    pa.field("estimated_departure_utc", pa.timestamp("us", tz="UTC")),
    pa.field("delay_minutes", pa.int32()),
    pa.field("diff_status", pa.string()),
    pa.field("is_on_time", pa.bool_()),
    pa.field("is_late_15", pa.bool_()),
    pa.field("is_late_60", pa.bool_()),
    pa.field("is_corridor", pa.bool_()),
])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    selected = select_files(RAW_DIR)
    print(f"Selected {len(selected)} file(s) (one per EST day) from {RAW_DIR}")

    all_rows: list[dict] = []

    for est_date, path in sorted(selected.items()):
        rows = flatten_file(path, est_date)
        all_rows.extend(rows)
        print(f"  {est_date}  {path.name}  → {len(rows):,} rows")

    if not all_rows:
        print("No rows produced — nothing to write.")
        return

    df = pd.DataFrame(all_rows)

    # Cast columns to the correct pandas dtypes before writing to Parquet
    df["scrape_date_est"] = pd.to_datetime(df["scrape_date_est"])
    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df["stop_sequence"] = df["stop_sequence"].astype("Int32")
    df["delay_minutes"] = df["delay_minutes"].astype("Int32")

    for col in ("scheduled_arrival_utc", "estimated_arrival_utc",
                "scheduled_departure_utc", "estimated_departure_utc"):
        df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")

    # Drop duplicates on the natural key
    df.drop_duplicates(
        subset=["train_key", "service_date", "station_code", "scrape_date_est"],
        keep="last",
        inplace=True,
    )

    table = pa.Table.from_pandas(df, schema=SCHEMA, preserve_index=False)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUTPUT_PATH)

    print(f"\nWrote {len(df):,} rows → {OUTPUT_PATH}")
    print(df.dtypes)


if __name__ == "__main__":
    main()
