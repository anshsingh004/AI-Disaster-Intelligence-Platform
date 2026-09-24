from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import random
import logging

from app.db import get_db
from app.schemas.disaster import DisasterInput, DisasterOutput, DisasterRecord
from app.schemas.alert import AlertRecord
from app.schemas.report import ReportRecord, ReportCreate
from app.services.ml_service import run_disaster_inference
from app.services.report_service import generate_report_content
from app.services.llm_service import generate_incident_sitrep, deterministic_fallback_sitrep
from app.core.response import success_response
from app.repositories.disaster_repository import DisasterRepository
from app.core.cache import get_cache, set_cache, invalidate_disaster_cache
from app.models.alert import Alert
from app.models.report import Report
from app.models.disaster import Disaster
from app.dependencies import get_current_user, RequireRole
from app.models.user import User

logger = logging.getLogger(__name__)

v1_router = APIRouter(prefix="/api/v1", tags=["Disaster Prediction v1"])
legacy_router = APIRouter(tags=["Disaster Prediction Legacy"])


def get_disaster_repo(db: Session = Depends(get_db)) -> DisasterRepository:
    """Dependency injection helper to obtain a DisasterRepository instance."""
    return DisasterRepository(db)


# ─────────────────────────────────────────────────────────────────────────────
# V1 Disaster Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@v1_router.post("/predict/disaster", response_model=dict, status_code=status.HTTP_201_CREATED)
@v1_router.post("/disasters", response_model=dict, status_code=status.HTTP_201_CREATED)
async def predict_disaster_v1(
    data: DisasterInput,
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    """
    AI-first incident pipeline: ingests sensor data, runs threat correlation,
    synthesizes a resilient Gemini SITREP with deterministic local fallback,
    persists disaster + linked alert records, auto-generates full structured reports
    for HIGH and CRITICAL risk incidents, and invalidates list caches.
    """
    # 1. Baseline correlation
    result = run_disaster_inference(data)

    # 2. Extract telemetry for SITREP synthesis
    raw_telemetry = data.raw_telemetry or {
        "rainfall": data.weather_rainfall,
        "wind_speed": data.weather_wind_speed,
        "social_score": data.social_signal_score,
    }

    # 3. Resilient SITREP generation (never raises 500; executes deterministic fallback on error)
    try:
        sitrep = await generate_incident_sitrep(
            telemetry_data=raw_telemetry,
            incident_type=result.disaster_type or "hazard",
            context_notes=f"Initial risk: {result.risk_level}. Location: {data.latitude:.4f}, {data.longitude:.4f}."
        )
    except Exception as e:
        logger.warning(f"Unexpected SITREP error in router: {e}. Executing deterministic fallback.")
        sitrep = deterministic_fallback_sitrep(raw_telemetry, result.disaster_type or "hazard")

    # 4. Integrate SITREP outputs
    if sitrep:
        result.sitrep_summary = sitrep.get("executive_summary")
        result.recommended_actions = sitrep.get("recommended_actions")
        if sitrep.get("risk_level") in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            result.risk_level = sitrep["risk_level"]

    # 5. Persist incident record
    db_record = repo.create(data, result)

    # 6. Invalidate cache on write
    invalidate_disaster_cache()

    # 7. Auto-generate structured report for HIGH and CRITICAL incidents
    if db_record.risk_level in ("HIGH", "CRITICAL"):
        try:
            risk_map = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
            report_code = f"AUTO-{db_record.id}-{random.randint(1000, 9999)}"
            content = generate_report_content(db_record)
            if sitrep and sitrep.get("situation_analysis"):
                content["situation_analysis"] = sitrep["situation_analysis"]
            if sitrep and sitrep.get("infrastructure_impact"):
                content["infrastructure_impact"] = sitrep["infrastructure_impact"]

            auto_report = Report(
                report_code=report_code,
                disaster_id=db_record.id,
                type=db_record.disaster_type.capitalize(),
                risk=risk_map.get(db_record.risk_level, "medium"),
                location=f"{db_record.latitude:.4f}°N, {db_record.longitude:.4f}°E",
                status="active",
                summary=db_record.sitrep_summary or content["executive_summary"][:500],
                **content,
            )
            repo.db.add(auto_report)
            repo.db.commit()
            logger.info(f"Auto-generated report {report_code} for {db_record.risk_level} disaster #{db_record.id}")
        except Exception as e:
            logger.error(f"Auto-report generation failed for disaster #{db_record.id}: {e}")
            # Non-fatal: incident creation still succeeds

    record_data = DisasterRecord.model_validate(db_record).model_dump(mode="json")
    return success_response(data=record_data)


@v1_router.get("/disasters", response_model=dict)
def get_disasters_v1(
    page: int = Query(1, ge=1, description="Page index (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Records limit per page"),
    disaster_type: Optional[str] = Query(None, description="Filter by disaster type (e.g. fire, flood)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk category (e.g. HIGH, MEDIUM)"),
    min_severity: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum severity score"),
    max_severity: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum severity score"),
    sort_by: str = Query("created_at", description="Field to sort results by"),
    order: str = Query("desc", description="Sort direction ('asc' or 'desc')"),
    search: Optional[str] = Query(None, description="Wildcard keyword search on disaster type"),
    refresh: Optional[bool] = Query(None, description="Force refresh to bypass and rebuild cache"),
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    """
    Queries operational disaster threat logs applying pagination, sorting, filters,
    and searches. Responses are cached dynamically.
    """
    # 1. Validate sorting fields to prevent injection or attribute errors
    allowed_sort_fields = {"created_at", "severity_score", "population_at_risk", "confidence"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_by field. Allowed fields: {allowed_sort_fields}"
        )

    if order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be 'asc' or 'desc'"
        )

    # 2. Build cache key
    cache_key = (
        f"disasters_list:page={page}:limit={limit}:type={disaster_type}:risk={risk_level}:"
        f"min={min_severity}:max={max_severity}:sort={sort_by}:order={order}:search={search}"
    )

    # 3. Check Cache (Bypass if refresh is True)
    if not refresh:
        cached_payload = get_cache(cache_key)
        if cached_payload:
            return success_response(data=cached_payload)

    # 4. Fetch results
    records, total = repo.get_paginated(
        page=page, limit=limit, disaster_type=disaster_type, risk_level=risk_level,
        min_severity=min_severity, max_severity=max_severity, sort_by=sort_by,
        order=order, search=search
    )

    # 5. Format payload
    records_data = [DisasterRecord.model_validate(r).model_dump(mode="json") for r in records]
    pages = (total + limit - 1) // limit

    paginated_data = {
        "items": records_data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

    # 6. Save in Cache (Expires in 5 minutes)
    set_cache(cache_key, paginated_data, expire_seconds=300)

    return success_response(data=paginated_data)


@v1_router.delete("/disasters/{disaster_id}", response_model=dict)
def delete_disaster(
    disaster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["EOC_LEAD", "ADMINISTRATOR"]))
):
    """
    Delete a disaster record by ID. Cascades to linked alerts and reports.
    Requires EOC_LEAD or ADMINISTRATOR role.
    """
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disaster record not found")

    db.delete(disaster)
    db.commit()
    invalidate_disaster_cache()
    return success_response(data={"id": disaster_id, "deleted": True})


@v1_router.patch("/disasters/{disaster_id}/acknowledge", response_model=dict)
@v1_router.post("/disasters/{disaster_id}/acknowledge", response_model=dict)
def acknowledge_disaster(
    disaster_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a disaster incident as acknowledged by operational staff."""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disaster record not found")

    disaster.acknowledged = True
    db.commit()
    db.refresh(disaster)
    invalidate_disaster_cache()

    return success_response(data={
        "id": disaster_id,
        "acknowledged": True,
        "title": disaster.title,
        "disaster_type": disaster.disaster_type
    })


# ─────────────────────────────────────────────────────────────────────────────
# V1 Alerts Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@v1_router.get("/alerts", response_model=dict)
def get_alerts(
    level: Optional[str] = Query(None, description="Filter by alert level (e.g. CRITICAL, HIGH)"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged state"),
    limit: int = Query(50, ge=1, le=200, description="Max number of alerts to return"),
    db: Session = Depends(get_db)
):
    """
    List all alerts ordered by creation date descending.
    Joins disaster type and severity from the linked disaster record.
    """
    query = db.query(Alert)

    if level:
        query = query.filter(Alert.level == level.upper())
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == acknowledged)

    total = query.count()
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()

    results = []
    for a in alerts:
        results.append({
            "id": a.id,
            "disaster_id": a.disaster_id,
            "level": a.level,
            "title": a.title,
            "description": a.description,
            "escalation_probability": a.escalation_probability,
            "acknowledged": a.acknowledged,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            # Joined from disaster relationship (lazy-loaded)
            "disaster_type": a.disaster.disaster_type if a.disaster else None,
            "severity_score": a.disaster.severity_score if a.disaster else None,
            "latitude": a.disaster.latitude if a.disaster else None,
            "longitude": a.disaster.longitude if a.disaster else None,
        })

    return success_response(data={"items": results, "total": total})


@v1_router.patch("/alerts/{alert_id}/acknowledge", response_model=dict)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a specific alert by ID. Requires authentication."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    alert.acknowledged = True
    db.commit()
    db.refresh(alert)

    return success_response(data={"id": alert_id, "acknowledged": True})


# ─────────────────────────────────────────────────────────────────────────────
# V1 Reports Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@v1_router.get("/reports", response_model=dict)
def get_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by report type"),
    risk: Optional[str] = Query(None, description="Filter by risk level (low/medium/high/critical)"),
    report_status: Optional[str] = Query(None, alias="status", description="Filter by status (active/monitoring/resolved)"),
    search: Optional[str] = Query(None, description="Search reports by type or location"),
    db: Session = Depends(get_db)
):
    """List reports with pagination and optional categorical filters."""
    query = db.query(Report)

    if type_filter:
        query = query.filter(Report.type.ilike(f"%{type_filter}%"))
    if risk:
        query = query.filter(Report.risk == risk.lower())
    if report_status:
        query = query.filter(Report.status == report_status.lower())
    if search:
        query = query.filter(
            Report.type.ilike(f"%{search}%") | Report.location.ilike(f"%{search}%")
        )

    total = query.count()
    offset = (page - 1) * limit
    reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
    pages = (total + limit - 1) // limit

    records = [ReportRecord.model_validate(r).model_dump(mode="json") for r in reports]
    return success_response(data={
        "items": records,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    })


@v1_router.post("/reports", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new report linked to a disaster record.
    Risk level is automatically derived from the linked disaster.
    AI-generated structured content (9 sections) is populated automatically.
    Requires authentication.
    """
    # Verify the linked disaster exists
    disaster = db.query(Disaster).filter(Disaster.id == data.disaster_id).first()
    if not disaster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disaster record not found. Select a valid disaster to link this report."
        )

    # Derive risk from disaster risk_level
    risk_map = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}
    risk = risk_map.get(disaster.risk_level, "medium")

    # Generate a unique report code
    report_code = f"RPT-{random.randint(1000, 9999)}"

    # Generate structured AI report content
    content = generate_report_content(disaster)

    report = Report(
        report_code=report_code,
        disaster_id=data.disaster_id,
        type=data.type,
        risk=risk,
        location=data.location,
        status="active",
        summary=data.summary or content["executive_summary"][:500],
        created_at=datetime.utcnow(),
        **content,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return success_response(data=ReportRecord.model_validate(report).model_dump(mode="json"))


@v1_router.delete("/reports/{report_id}", response_model=dict)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole(["EOC_LEAD", "ADMINISTRATOR"]))
):
    """Delete a report by ID. Requires EOC_LEAD or ADMINISTRATOR role."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    db.delete(report)
    db.commit()
    return success_response(data={"id": report_id, "deleted": True})


# ─────────────────────────────────────────────────────────────────────────────
# Legacy REST APIs (Backward Compatible, Unwrapped)
# ─────────────────────────────────────────────────────────────────────────────

@legacy_router.post("/predict/disaster", response_model=DisasterOutput)
async def predict_disaster_legacy(
    data: DisasterInput,
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    result = run_disaster_inference(data)
    raw_telemetry = data.raw_telemetry or {
        "rainfall": data.weather_rainfall,
        "wind_speed": data.weather_wind_speed,
        "social_score": data.social_signal_score,
    }
    try:
        sitrep = await generate_incident_sitrep(raw_telemetry, result.disaster_type or "hazard")
        if sitrep:
            result.sitrep_summary = sitrep.get("executive_summary")
            result.recommended_actions = sitrep.get("recommended_actions")
            if sitrep.get("risk_level") in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
                result.risk_level = sitrep["risk_level"]
    except Exception:
        fallback = deterministic_fallback_sitrep(raw_telemetry, result.disaster_type or "hazard")
        result.sitrep_summary = fallback.get("executive_summary")
        result.recommended_actions = fallback.get("recommended_actions")

    repo.create(data, result)
    invalidate_disaster_cache()
    return result


@legacy_router.get("/disasters", response_model=List[DisasterRecord])
def get_disasters_legacy(
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    return repo.get_all()
