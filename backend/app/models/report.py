from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String, nullable=False, unique=True, index=True)
    disaster_id = Column(Integer, ForeignKey("disasters.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    risk = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    summary = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship back to Disaster model
    disaster = relationship("Disaster", backref="reports")

    __table_args__ = (
        CheckConstraint("risk IN ('low', 'medium', 'high', 'critical')", name="check_report_risk_values"),
        CheckConstraint("status IN ('active', 'monitoring', 'resolved')", name="check_report_status_values"),
    )
