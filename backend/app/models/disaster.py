from sqlalchemy import Column, Integer, Float, String, DateTime
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
