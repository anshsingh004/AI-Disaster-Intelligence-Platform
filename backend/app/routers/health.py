from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.db import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Diagnostics"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/readiness")
def readiness_check(db: Session = Depends(get_db)):
    try:
        # Check database connection viability
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Database readiness check failed: {str(e)}")
        return {"status": "unready", "database": "disconnected"}
