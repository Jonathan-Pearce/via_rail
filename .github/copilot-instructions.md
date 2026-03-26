# Via Rail Train Performance — Project Instructions

## What This Project Does

Scrapes Via Rail live train tracking data (https://tsimobile.viarail.ca/data/allData.json) on a daily cron schedule, runs a cleaning pipeline to produce a master Parquet dataset, and serves a FastAPI + React dashboard with ML-powered arrival predictions.

## Directory Structure

```
raw_data/          # Raw JSON snapshots from the scraper (one file per scrape run)
clean_data/        # Cleaned Parquet dataset output
  build_historical.py   # One-time script: processes all raw_data/ into master Parquet
  via_rail_clean.parquet  # Master cleaned dataset
backend/           # FastAPI app
  app/
    main.py        # FastAPI entrypoint
    data_loader.py # Parquet loading + query helpers
    routers/       # Endpoint modules (performance, stations, live, predict)
frontend/          # Vite + TypeScript React app
  src/
    components/    # Reusable UI components
    pages/         # Tab 1 (Performance), Tab 2 (Map)
    api/           # API client hooks
models/            # Trained ML model artifacts (arrival_model.joblib)
save_via_data.py   # Scraper script (runs on cron)
update_dataset.py  # Daily incremental Parquet update (runs after scraper)
```

## Raw JSON Schema

Each raw JSON file is a single object. Keys are `"{train_number} ({MM-DD})"` for multi-day trains (e.g., `"2 (03-28)"`) or just `"{train_number}"` for same-day trains (e.g., `"20"`).

Each train object has:
```json
{
  "departed": true,
  "arrived": false,
  "from": "TORONTO",
  "to": "MONTRÉAL",
  "instance": "2025-04-01",    // ISO date string of the service date
  "times": [ ...stops ]
}
```

Each stop in `times[]`:
```json
{
  "station": "Kingston",
  "code": "KGON",
  "estimated": "2025-04-01T17:45:00Z",   // current ETA (UTC ISO string)
  "scheduled": "2025-04-01T17:15:00Z",   // original scheduled time (UTC ISO string)
  "eta": "ARR",                          // "ARR" = this is an arrival time
  "arrival": {                           // optional — absent on origin stop
    "estimated": "2025-04-01T17:45:00Z",
    "scheduled": "2025-04-01T17:15:00Z"
  },
  "departure": {                         // present on all stops except final destination
    "estimated": "2025-04-01T17:47:00Z",
    "scheduled": "2025-04-01T17:17:00Z"
  },
  "diff": "med",      // "goo" = on time/early, "med" = moderately late, "bad" = very late, null = unknown
  "diffMin": 30       // integer delay in minutes (negative = early, 0 = on time)
}
```

## File Selection Rule (Critical)

Scrapes run at ~03:00–04:30 UTC, which is ~22:00–00:30 EST. The Via Rail website resets at midnight EST. To capture the final state of each day's trains, we select **one file per EST calendar day**: the latest scrape file whose UTC timestamp converts to that EST date.

```python
EST = timezone(timedelta(hours=-5))
dt_utc = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
est_date = dt_utc.astimezone(EST).date()  # groups files to EST calendar days
# Then pick the max(dt_utc) per est_date
```

## Clean Dataset Schema

`clean_data/via_rail_clean.parquet` — one row per (train stop × scrape day):

| Column | Type | Description |
|--------|------|-------------|
| `scrape_date_est` | date | EST calendar date of the selected scrape file |
| `train_key` | str | Raw key from JSON (e.g., `"60"`, `"2 (03-28)"`) |
| `train_number` | str | Just the numeric part (e.g., `"60"`, `"2"`) |
| `service_date` | date | Date from `instance` field |
| `origin` | str | Train origin city (from `from`) |
| `destination` | str | Train destination city (from `to`) |
| `departed` | bool | Whether train has departed origin |
| `arrived` | bool | Whether train has reached destination |
| `stop_sequence` | int | 0-based index of this stop in the journey |
| `station_name` | str | Station display name |
| `station_code` | str | 4-letter station code |
| `scheduled_arrival_utc` | datetime | `arrival.scheduled` (null for origin) |
| `estimated_arrival_utc` | datetime | `arrival.estimated` (null for origin) |
| `scheduled_departure_utc` | datetime | `departure.scheduled` (null for terminus) |
| `estimated_departure_utc` | datetime | `departure.estimated` (null for terminus) |
| `delay_minutes` | int | `diffMin` from JSON |
| `diff_status` | str | `diff` from JSON (`goo`/`med`/`bad`/null) |
| `is_on_time` | bool | `delay_minutes <= 5` |
| `is_late_15` | bool | `delay_minutes >= 15` |
| `is_late_60` | bool | `delay_minutes >= 60` |
| `is_corridor` | bool | Whether this stop is on the Windsor–Québec corridor |

## Windsor–Québec City Corridor

Corridor station codes (used for `is_corridor` flag and filtering):
```python
CORRIDOR_STATION_CODES = {
    'WDON', 'CHAT', 'GLNC', 'LNDN', 'INGR', 'WDST', 'BRTF', 'ALDR',
    'OAKV', 'TRTO', 'GUIL', 'OSHA', 'CBRG', 'PHOP', 'TRNJ', 'BLVL',
    'NAPN', 'KGON', 'GANA', 'BRKV', 'CWLL', 'ALEX', 'CSLM', 'OTTW',
    'FALL', 'SMTF', 'SLAM', 'MTRL', 'DORV', 'COTO', 'SHYA', 'DRMV',
    'SFOY', 'QBEC', 'CHNY',
}
```

Corridor routes (from/to pairs that constitute Windsor–Québec operations):
- Windsor ↔ Toronto, Toronto ↔ Ottawa, Ottawa ↔ Québec
- Toronto ↔ Montréal, Montréal ↔ Québec, Ottawa ↔ Montréal

## Tech Stack

| Layer | Choice |
|-------|--------|
| Data storage | Apache Parquet (via `pyarrow` / `pandas`) |
| Backend | FastAPI + Uvicorn |
| Frontend | Vite + TypeScript + React |
| Map | React Leaflet |
| Charts | Recharts |
| ML | scikit-learn / XGBoost / LightGBM |
| Deployment | Docker + Docker Compose; cloud target: Railway.app or Render |

## Key Conventions

- All timestamps stored as UTC in the Parquet — convert to EST in the API/frontend for display.
- Negative `delay_minutes` means the train is running early; treat as `delay_minutes = 0` for performance categorization.
- `diff` status mapping: `"goo"` = ≤5 min, `"med"` = 6–59 min, `"bad"` = ≥60 min, `null` = not yet departed or unknown.
- The scraper (`save_via_data.py`) must not be modified unless the task explicitly requires it.
- All new Python code uses `pyarrow` + `pandas` for Parquet I/O.
- All times in API responses are ISO 8601 strings in UTC; the frontend handles display timezone conversion.

## Build & Run

```bash
# Install Python deps
pip install -r requirements.txt

# Build full historical dataset from all raw_data/ JSONs (run once)
python clean_data/build_historical.py

# Daily update (run after scraper)
python update_dataset.py

# Start backend dev server
cd backend && uvicorn app.main:app --reload

# Start frontend dev server
cd frontend && npm install && npm run dev
```
