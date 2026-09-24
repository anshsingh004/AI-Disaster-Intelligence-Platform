from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any, Dict, Union


class DisasterInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude coordinate")
    timestamp: Optional[datetime] = None
    weather_rainfall: Optional[float] = Field(default=0.0, description="Rainfall telemetry in mm/h")
    weather_wind_speed: Optional[float] = Field(default=0.0, description="Wind speed telemetry in km/h")
    social_signal_score: Optional[float] = Field(default=0.0, ge=0.0, le=1.0, description="Citizen report intensity 0-1")
    title: Optional[str] = Field(default=None, max_length=255, description="Operational incident title")
    source_origin: Optional[str] = Field(default="MANUAL", description="Telemetry ingestion origin")
    raw_telemetry: Optional[Dict[str, Any]] = None


class DisasterOutput(BaseModel):
    disaster_type: str
    risk_level: str
    title: Optional[str] = None
    sitrep_summary: Optional[str] = None
    recommended_actions: Optional[Union[List[str], Dict[str, Any]]] = None
    severity_score: Optional[float] = None
    population_at_risk: Optional[int] = None
    confidence: Optional[float] = None
    timestamp: datetime


class DisasterRecord(BaseModel):
    id: int
    title: Optional[str] = None
    disaster_type: str
    risk_level: str
    latitude: float
    longitude: float
    raw_telemetry: Optional[Dict[str, Any]] = None
    sitrep_summary: Optional[str] = None
    recommended_actions: Optional[Union[List[str], Dict[str, Any]]] = None
    source_origin: Optional[str] = "MANUAL"
    acknowledged: bool = False
    created_at: datetime

    # Retained optional attributes for backwards-compatible response envelopes
    severity_score: Optional[float] = None
    population_at_risk: Optional[int] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class DisasterPaginationResponse(BaseModel):
    """Schema wrapping paginated lists of disaster records with execution metadata."""
    items: List[DisasterRecord]
    total: int
    page: int
    limit: int
    pages: int
