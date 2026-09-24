from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    CheckConstraint,
)
from app.db import Base


class Disaster(Base):
    __tablename__ = "disasters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True, index=True)
    disaster_type = Column(String(50), nullable=False, index=True)
    risk_level = Column(String(20), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Real-time telemetry and operational tracking
    raw_telemetry = Column(JSON, nullable=True)
    sitrep_summary = Column(Text, nullable=True)
    recommended_actions = Column(JSON, nullable=True)
    source_origin = Column(String(50), default="MANUAL", nullable=True)
    acknowledged = Column(Boolean, default=False, nullable=False, index=True)

    # Legacy fields maintained with nullable defaults for schema transition compatibility
    severity_score = Column(Float, nullable=True)
    population_at_risk = Column(Integer, nullable=True)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        CheckConstraint("latitude >= -90.0 AND latitude <= 90.0", name="check_latitude_bounds"),
        CheckConstraint("longitude >= -180.0 AND longitude <= 180.0", name="check_longitude_bounds"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="check_risk_level_values"),
        CheckConstraint("severity_score IS NULL OR (severity_score >= 0.0 AND severity_score <= 1.0)", name="check_severity_bounds"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0.0 AND confidence <= 1.0)", name="check_confidence_bounds"),
        CheckConstraint("population_at_risk IS NULL OR population_at_risk >= 0", name="check_population_bounds"),
    )
