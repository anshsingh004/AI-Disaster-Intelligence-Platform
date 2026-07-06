from pydantic import BaseModel
from datetime import datetime
from typing import List

class DisasterInput(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    weather_rainfall: float
    weather_wind_speed: float
    social_signal_score: float

class DisasterOutput(BaseModel):
    disaster_type: str
    severity_score: float
    risk_level: str
    population_at_risk: int
    confidence: float
    timestamp: datetime

class DisasterRecord(BaseModel):
    id: int
    disaster_type: str
    severity_score: float
    risk_level: str
    population_at_risk: int
    confidence: float
    latitude: float
    longitude: float
    created_at: datetime

    class Config:
        from_attributes = True

class DisasterPaginationResponse(BaseModel):
    """Schema wrapping paginated lists of disaster records with execution metadata."""
    items: List[DisasterRecord]
    total: int
    page: int
    limit: int
    pages: int
