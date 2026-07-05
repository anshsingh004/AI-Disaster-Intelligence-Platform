from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DisasterInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    timestamp: datetime = Field(..., description="Timestamp of threat detection")
    weather_rainfall: Optional[float] = Field(default=None, ge=0.0, description="Rainfall signal in mm")
    weather_wind_speed: Optional[float] = Field(default=None, ge=0.0, description="Wind speed signal in km/h")
    social_signal_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Social signal score")

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
        # Pydantic v2 configuration compatibility for ORM mapping
