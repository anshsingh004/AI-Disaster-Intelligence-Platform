from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.disaster import Disaster
from app.schemas.disaster import DisasterInput, DisasterOutput, DisasterRecord
from app.services.ml_service import run_disaster_inference
from app.core.response import success_response

v1_router = APIRouter(prefix="/api/v1", tags=["Disaster Prediction v1"])
legacy_router = APIRouter(tags=["Disaster Prediction Legacy"])

def create_disaster_record(db: Session, data: DisasterInput, result: DisasterOutput) -> Disaster:
    db_disaster = Disaster(
        disaster_type=result.disaster_type,
        severity_score=result.severity_score,
        risk_level=result.risk_level,
        population_at_risk=result.population_at_risk,
        confidence=result.confidence,
        latitude=data.latitude,
        longitude=data.longitude,
        created_at=result.timestamp
    )
    db.add(db_disaster)
    db.commit()
    db.refresh(db_disaster)
    return db_disaster

# --- V1 REST APIs (Standard Envelope Wrapped) ---

@v1_router.post("/predict/disaster", response_model=dict)
def predict_disaster_v1(data: DisasterInput, db: Session = Depends(get_db)):
    result = run_disaster_inference(data)
    db_record = create_disaster_record(db, data, result)
    record_data = DisasterRecord.model_validate(db_record).model_dump()
    return success_response(data=record_data)

@v1_router.get("/disasters", response_model=dict)
def get_disasters_v1(db: Session = Depends(get_db)):
    records = db.query(Disaster).order_by(Disaster.created_at.desc()).all()
    records_data = [DisasterRecord.model_validate(r).model_dump() for r in records]
    return success_response(data=records_data)

# --- Legacy REST APIs (Backward Compatible, Unwrapped) ---

@legacy_router.post("/predict/disaster", response_model=DisasterOutput)
def predict_disaster_legacy(data: DisasterInput, db: Session = Depends(get_db)):
    result = run_disaster_inference(data)
    create_disaster_record(db, data, result)
    return result

@legacy_router.get("/disasters", response_model=List[DisasterRecord])
def get_disasters_legacy(db: Session = Depends(get_db)):
    records = db.query(Disaster).order_by(Disaster.created_at.desc()).all()
    return records
