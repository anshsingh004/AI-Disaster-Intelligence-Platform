from sqlalchemy import Column, Integer, Float, String, DateTime, CheckConstraint
from datetime import datetime
from app.db import Base

class Disaster(Base):
    __tablename__ = "disasters"

    id = Column(Integer, primary_key=True, index=True)
    disaster_type = Column(String, nullable=False, index=True)
    severity_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False, index=True)
    population_at_risk = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        CheckConstraint("latitude >= -90.0 AND latitude <= 90.0", name="check_latitude_bounds"),
        CheckConstraint("longitude >= -180.0 AND longitude <= 180.0", name="check_longitude_bounds"),
        CheckConstraint("severity_score >= 0.0 AND severity_score <= 1.0", name="check_severity_bounds"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="check_confidence_bounds"),
        CheckConstraint("population_at_risk >= 0", name="check_population_bounds"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="check_risk_level_values"),
    )
