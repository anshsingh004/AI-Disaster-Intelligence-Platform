from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.schemas.disaster import DisasterInput, DisasterOutput, DisasterRecord
from app.services.ml_service import run_disaster_inference
from app.core.response import success_response
from app.repositories.disaster_repository import DisasterRepository

v1_router = APIRouter(prefix="/api/v1", tags=["Disaster Prediction v1"])
legacy_router = APIRouter(tags=["Disaster Prediction Legacy"])

def get_disaster_repo(db: Session = Depends(get_db)) -> DisasterRepository:
    """Dependency injection helper to obtain a DisasterRepository instance."""
    return DisasterRepository(db)

# --- V1 REST APIs (Standard Envelope Wrapped) ---

@v1_router.post("/predict/disaster", response_model=dict)
def predict_disaster_v1(
    data: DisasterInput,
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    result = run_disaster_inference(data)
    db_record = repo.create(data, result)
    record_data = DisasterRecord.model_validate(db_record).model_dump()
    return success_response(data=record_data)

@v1_router.get("/disasters", response_model=dict)
def get_disasters_v1(
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    records = repo.get_all()
    records_data = [DisasterRecord.model_validate(r).model_dump() for r in records]
    return success_response(data=records_data)

# --- Legacy REST APIs (Backward Compatible, Unwrapped) ---

@legacy_router.post("/predict/disaster", response_model=DisasterOutput)
def predict_disaster_legacy(
    data: DisasterInput,
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    result = run_disaster_inference(data)
    repo.create(data, result)
    return result

@legacy_router.get("/disasters", response_model=List[DisasterRecord])
def get_disasters_legacy(
    repo: DisasterRepository = Depends(get_disaster_repo)
):
    return repo.get_all()
