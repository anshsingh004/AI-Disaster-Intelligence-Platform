from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db import Base


class KnowledgeBase(Base):
    """
    KnowledgeBase entity storing standard operating procedures, historical event logs,
    and mitigation manuals for RAG intelligence synthesis.
    """
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
