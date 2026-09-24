from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ReportRecord(BaseModel):
    id: int
    report_code: str
    disaster_id: int
    type: str
    risk: str
    location: str
    status: str
    summary: Optional[str] = None
    created_at: datetime

    # AI-generated structured sections
    executive_summary: Optional[str] = None
    situation_analysis: Optional[str] = None
    disaster_classification: Optional[str] = None
    risk_assessment: Optional[str] = None
    population_impact: Optional[str] = None
    infrastructure_impact: Optional[str] = None
    ai_confidence_note: Optional[str] = None
    forecast: Optional[str] = None
    recommended_actions: Optional[str] = None
    data_sources: Optional[str] = None

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    disaster_id: int
    type: str = Field(..., description="Type of disaster (e.g. Wildfire, Flood, Earthquake)")
    location: str = Field(..., min_length=2, max_length=200)
    summary: Optional[str] = Field(None, max_length=1000)

