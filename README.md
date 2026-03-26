# Via Rail Train Performance

Automated collection, cleaning, and analysis of Via Rail train tracking data for the Windsor–Québec City corridor and Canada-wide routes.

## What This Project Does

1. **Scrapes** live train tracking data from the Via Rail API on a nightly cron schedule
2. **Cleans** raw JSON snapshots into a master Parquet dataset with computed performance metrics
3. **Serves** a FastAPI + React dashboard with historical performance charts and a live train map
4. **Predicts** train arrival times using an ML model trained on historical delay data

## Stack

- **Data**: Apache Parquet (`pyarrow` / `pandas`)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Vite + TypeScript + React, React Leaflet, Recharts
- **ML**: scikit-learn / XGBoost / LightGBM
- **Deployment**: Docker + Docker Compose (target: Railway.app / Render)

## Quick Start

```bash
pip install -r requirements.txt

# Build the full historical dataset (run once)
python clean_data/build_historical.py

# Daily incremental update (run after nightly scrape)
python update_dataset.py

# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend
cd frontend && npm install && npm run dev
```

## Project Roadmap

See the [Issues tab](../../issues) for the full implementation plan, organized by phase:

- **Phase 1 — Data Pipeline**: Historical cleaning, daily updates, corridor filtering
- **Phase 2 — Backend API**: FastAPI endpoints for performance, stations, live data, predictions
- **Phase 3 — Frontend Dashboard**: Performance charts (Tab 1), live map (Tab 2)
- **Phase 4 — ML Prediction**: Feature engineering, model training, live prediction endpoint
- **Phase 5 — Deployment**: Docker, CI/CD, cloud hosting
