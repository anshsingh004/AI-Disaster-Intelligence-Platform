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

    class Config:
        from_attributes = True


class ReportCreate(BaseModel):
    disaster_id: int
    type: str = Field(..., description="Type of disaster (e.g. Wildfire, Flood, Earthquake)")
    location: str = Field(..., min_length=2, max_length=200)
    summary: Optional[str] = Field(None, max_length=1000)
