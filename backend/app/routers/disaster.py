from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.schemas.disaster import DisasterInput, DisasterOutput, DisasterRecord
from app.services.ml_service import run_disaster_inference
from app.core.response import success_response
from app.repositories.disaster_repository import DisasterRepository
from app.core.cache import get_cache, set_cache, invalidate_disaster_cache

v1_router = APIRouter(prefix="/api/v1", tags=["Disaster Prediction v1"])
legacy_router = APIRouter(tags=["Disaster Prediction Legacy"])

def get_disaster_repo(db: Session = Depends(get_db)) -> DisasterRepository:
    """Dependency injection helper to obtain a DisasterRepository instance."""
    return DisasterRepository(db)

# --- V1 REST APIs (Standard Envelope Wrapped) ---

@v1_router.post("/predict/disaster", response_model=dict, status_code=status.HTTP_201_CREATED)
def predict_disaster_v1(
    data: DisasterInput,
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    """
    Ingests weather metrics and social sentiment, computes hazard scores,
    persists the prediction log record, and invalidates list caches.
    """
    result = run_disaster_inference(data)
    db_record = repo.create(data, result)
    
    # Invalidate cache on write
    invalidate_disaster_cache()
    
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

    # 3. Check Cache
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

# --- Legacy REST APIs (Backward Compatible, Unwrapped) ---

@legacy_router.post("/predict/disaster", response_model=DisasterOutput)
def predict_disaster_legacy(
    data: DisasterInput,
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    result = run_disaster_inference(data)
    repo.create(data, result)
    invalidate_disaster_cache()
    return result

@legacy_router.get("/disasters", response_model=List[DisasterRecord])
def get_disasters_legacy(
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    return repo.get_all()
