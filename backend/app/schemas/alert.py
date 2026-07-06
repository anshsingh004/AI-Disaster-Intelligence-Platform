from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AlertRecord(BaseModel):
    id: int
    disaster_id: int
    level: str
    title: str
    description: Optional[str] = None
    escalation_probability: float
    acknowledged: bool
    created_at: datetime
    # Joined from linked disaster record
    disaster_type: Optional[str] = None
    severity_score: Optional[float] = None

    class Config:
        from_attributes = True
