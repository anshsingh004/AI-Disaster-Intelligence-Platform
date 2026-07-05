from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    disaster_id = Column(Integer, ForeignKey("disasters.id", ondelete="CASCADE"), nullable=False, index=True)
    level = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    escalation_probability = Column(Float, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationship back to Disaster model
    disaster = relationship("Disaster", backref="alerts")

    __table_args__ = (
        CheckConstraint("escalation_probability >= 0.0 AND escalation_probability <= 100.0", name="check_escalation_bounds"),
        CheckConstraint("level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')", name="check_alert_level_values"),
    )
