"""
live.py — Live train positions and delays (proxies the Via Rail API).

GET /api/live
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["live"])

_VIA_RAIL_URL = "https://tsimobile.viarail.ca/data/allData.json"


@router.get("/live")
def get_live() -> dict[str, Any]:
    """
    Proxy the Via Rail live tracking API and return a simplified payload.

    Response shape:
        {
            "trains": [
                {
                    "train_key": "60",
                    "from": "TORONTO",
                    "to": "MONTRÉAL",
                    "departed": true,
                    "arrived": false,
                    "service_date": "2025-04-01",
                    "stops": [
                        {
                            "station": "Kingston",
                            "code": "KGON",
                            "diff_status": "med",
                            "delay_minutes": 12,
                            "estimated_arrival": "2025-04-01T17:45:00Z",
                            "scheduled_arrival": "2025-04-01T17:33:00Z"
                        },
                        ...
                    ]
                },
                ...
            ]
        }
    """
    try:
        response = httpx.get(_VIA_RAIL_URL, timeout=10.0)
        response.raise_for_status()
        raw: dict = response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Via Rail API error: {exc}") from exc

    trains = []
    for train_key, train in raw.items():
        stops = []
        for stop in train.get("times", []):
            arrival = stop.get("arrival") or {}
            stops.append({
                "station": stop.get("station"),
                "code": stop.get("code"),
                "diff_status": stop.get("diff"),
                "delay_minutes": stop.get("diffMin"),
                "estimated_arrival": arrival.get("estimated"),
                "scheduled_arrival": arrival.get("scheduled"),
            })

        trains.append({
            "train_key": train_key,
            "from": train.get("from"),
            "to": train.get("to"),
            "departed": bool(train.get("departed", False)),
            "arrived": bool(train.get("arrived", False)),
            "service_date": train.get("instance"),
            "stops": stops,
        })

    return {"trains": trains}
