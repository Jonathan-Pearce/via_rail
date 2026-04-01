"""
update_dataset.py — Incremental daily update for clean_data/via_rail_clean.parquet.

Selects the latest scrape file for TODAY's EST date, parses it into the
canonical schema, appends to the master Parquet, and deduplicates so the
script is safe to run multiple times on the same day.

Cron usage:
    30 4 * * * python /path/to/save_via_data.py && python /path/to/update_dataset.py
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
RAW_DIR = REPO_ROOT / "raw_data"
OUTPUT_PATH = REPO_ROOT / "clean_data" / "via_rail_clean.parquet"

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
# File selection: latest file for the given EST date
# ---------------------------------------------------------------------------
def select_file_for_date(raw_dir: Path, target_est: date) -> Path | None:
    """
    Return the path to the latest scrape file whose UTC timestamp falls on
    *target_est* when converted to EST, or None if no such file exists.
    """
    best_ts: datetime | None = None
    best_path: Path | None = None

    for path in raw_dir.glob("Via_data_*.json"):
        ts_utc = parse_utc_timestamp(path.name)
        if ts_utc is None:
            continue
        if ts_utc.astimezone(EST).date() != target_est:
            continue
        if best_ts is None or ts_utc > best_ts:
            best_ts = ts_utc
            best_path = path

    return best_path


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
        train_number = train_key.split()[0]

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

# Columns used to identify a unique stop record
DEDUP_KEYS = ["train_key", "service_date", "station_code", "scrape_date_est"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    today_est = datetime.now(UTC).astimezone(EST).date()
    print(f"Today's EST date: {today_est}")

    path = select_file_for_date(RAW_DIR, today_est)
    if path is None:
        print(f"No scrape file found for {today_est} — nothing to do.")
        return

    print(f"Selected file: {path.name}")

    new_rows = flatten_file(path, today_est)
    if not new_rows:
        print("File produced 0 rows — nothing to append.")
        return

    new_df = pd.DataFrame(new_rows)
    new_df["stop_sequence"] = new_df["stop_sequence"].astype("Int32")
    new_df["delay_minutes"] = new_df["delay_minutes"].astype("Int32")
    for col in ("scheduled_arrival_utc", "estimated_arrival_utc",
                "scheduled_departure_utc", "estimated_departure_utc"):
        new_df[col] = pd.to_datetime(new_df[col], utc=True, errors="coerce")

    # Load existing dataset (if present) and combine
    if OUTPUT_PATH.exists():
        existing_df = pq.read_table(OUTPUT_PATH).to_pandas()
        existing_count = len(existing_df)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        existing_count = 0
        combined_df = new_df.copy()

    # Normalise date columns so dedup key comparison works regardless of
    # whether values came from the existing Parquet (Python date objects) or
    # from the freshly-parsed DataFrame (datetime64).
    combined_df["scrape_date_est"] = pd.to_datetime(combined_df["scrape_date_est"])
    combined_df["service_date"] = pd.to_datetime(combined_df["service_date"], errors="coerce")

    # Deduplicate — safe to run multiple times per day
    combined_df.drop_duplicates(
        subset=DEDUP_KEYS,
        keep="last",
        inplace=True,
    )

    rows_added = len(combined_df) - existing_count

    table = pa.Table.from_pandas(combined_df, schema=SCHEMA, preserve_index=False)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, OUTPUT_PATH)

    print(
        f"Added {rows_added:,} new rows — "
        f"total {len(combined_df):,} rows in {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
