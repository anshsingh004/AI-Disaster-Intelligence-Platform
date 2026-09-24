import logging
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.disaster import Disaster
from app.models.alert import Alert
from app.models.report import Report
from app.schemas.disaster import DisasterRecord
from app.services.feed_service import fetch_usgs_earthquakes, fetch_weather_telemetry
from app.services.llm_service import generate_incident_sitrep, deterministic_fallback_sitrep
from app.services.report_service import generate_report_content
from app.core.cache import invalidate_disaster_cache
from app.core.response import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/feeds", tags=["Public Telemetry Feeds"])


@router.post("/scan", response_model=dict, status_code=status.HTTP_200_OK)
async def scan_public_feeds(
    min_magnitude: float = Query(1.0, ge=0.0, le=10.0, description="Minimum earthquake magnitude threshold"),
    enrich_weather: bool = Query(True, description="Query Open-Meteo atmospheric readings for incident coordinates"),
    db: Session = Depends(get_db)
):
    """
    On-demand public telemetry ingestion pipeline:
    1. Queries free live USGS GeoJSON feeds with 5s timeout.
    2. Identifies new emergency events not present in the last 6 hours (deduplication).
    3. Enriches telemetry with Open-Meteo weather data.
    4. Synthesizes tactical SITREPs using Gemini with deterministic fallback.
    5. Persists new disaster entities, alerts, and automated reports.
    """
    # 1. Fetch raw live features from USGS
    events = await fetch_usgs_earthquakes(min_magnitude=min_magnitude)

    # 2. Query existing disasters from the last 6 hours for deduplication
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=6)
    existing_records = db.query(Disaster.title, Disaster.latitude, Disaster.longitude).filter(
        Disaster.created_at >= cutoff_time
    ).all()

    existing_titles = {rec[0] for rec in existing_records if rec[0]}
    existing_coords = {(round(rec[1], 2), round(rec[2], 2)) for rec in existing_records}

    new_disasters: List[dict] = []

    for event in events:
        title = event["title"]
        lat = event["latitude"]
        lon = event["longitude"]
        coord_key = (round(lat, 2), round(lon, 2))

        # Skip duplicate occurrences
        if title in existing_titles or coord_key in existing_coords:
            continue

        existing_titles.add(title)
        existing_coords.add(coord_key)

        # 3. Weather enrichment (Open-Meteo)
        raw_telemetry = dict(event["raw_telemetry"])
        if enrich_weather:
            weather_data = await fetch_weather_telemetry(lat, lon)
            raw_telemetry.update(weather_data)

        # 4. Generate Situation Report (SITREP) with automatic fallback
        try:
            sitrep = await generate_incident_sitrep(
                telemetry_data=raw_telemetry,
                incident_type="earthquake",
                context_notes=f"Public telemetry source: USGS. Event: {title}"
            )
        except Exception as e:
            logger.warning(f"SITREP synthesis error for feed event {title}: {e}")
            sitrep = deterministic_fallback_sitrep(raw_telemetry, "earthquake")

        risk_level = sitrep.get("risk_level", "MEDIUM")
        if risk_level not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            risk_level = "MEDIUM"

        # 5. Persist to database
        db_disaster = Disaster(
            title=title,
            disaster_type="earthquake",
            risk_level=risk_level,
            latitude=lat,
            longitude=lon,
            raw_telemetry=raw_telemetry,
            sitrep_summary=sitrep.get("executive_summary"),
            recommended_actions=sitrep.get("recommended_actions"),
            source_origin="USGS",
            acknowledged=False,
            severity_score=0.85 if risk_level in ("HIGH", "CRITICAL") else 0.45,
            confidence=0.92,
            population_at_risk=35000 if risk_level in ("HIGH", "CRITICAL") else 5000,
            created_at=datetime.now(timezone.utc),
        )
        db.add(db_disaster)
        db.flush()

        # Create linked alert
        alert = Alert(
            disaster_id=db_disaster.id,
            level=db_disaster.risk_level,
            title=f"{db_disaster.risk_level} Seismic Alert: {title}",
            description=(
                db_disaster.sitrep_summary
                or f"USGS seismic telemetry detected {title} at coordinates {lat:.4f}, {lon:.4f}."
            ),
            escalation_probability=85.0 if risk_level in ("HIGH", "CRITICAL") else 40.0,
            acknowledged=False,
            created_at=db_disaster.created_at,
        )
        db.add(alert)

        # Auto-generate report for HIGH and CRITICAL incidents
        if db_disaster.risk_level in ("HIGH", "CRITICAL"):
            try:
                risk_map = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
                report_code = f"AUTO-USGS-{db_disaster.id}-{random.randint(1000, 9999)}"
                content = generate_report_content(db_disaster)
                if sitrep.get("situation_analysis"):
                    content["situation_analysis"] = sitrep["situation_analysis"]
                if sitrep.get("infrastructure_impact"):
                    content["infrastructure_impact"] = sitrep["infrastructure_impact"]

                auto_report = Report(
                    report_code=report_code,
                    disaster_id=db_disaster.id,
                    type="Earthquake",
                    risk=risk_map.get(db_disaster.risk_level, "medium"),
                    location=f"{db_disaster.latitude:.4f}°N, {db_disaster.longitude:.4f}°E",
                    status="active",
                    summary=db_disaster.sitrep_summary or content["executive_summary"][:500],
                    **content,
                )
                db.add(auto_report)
            except Exception as e:
                logger.error(f"Auto-report generation failed for feed incident #{db_disaster.id}: {e}")

        serialized = DisasterRecord.model_validate(db_disaster).model_dump(mode="json")
        new_disasters.append(serialized)

    db.commit()
    if new_disasters:
        invalidate_disaster_cache()

    return success_response(data={
        "scanned": len(events),
        "new_ingested": len(new_disasters),
        "events": new_disasters
    })


@router.get("/weather", response_model=dict)
async def get_live_weather(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate")
):
    """
    On-demand atmospheric telemetry query via Open-Meteo.
    Returns real-time precipitation, wind speed, temperature, and humidity.
    """
    data = await fetch_weather_telemetry(lat, lon)
    return success_response(data=data)
