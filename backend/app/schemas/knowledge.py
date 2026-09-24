from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class KnowledgeBaseCreate(BaseModel):
    title: str = Field(..., max_length=255, description="Document or SOP title")
    category: str = Field(..., max_length=100, description="Category (e.g. SOP, Mitigation, History)")
    content: str = Field(..., description="Document content and operational text")
    source_url: Optional[str] = Field(None, max_length=500, description="Optional reference or manual link")


class KnowledgeBaseRecord(BaseModel):
    id: int
    title: str
    category: str
    content: str
    source_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
