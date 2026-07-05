from sqlalchemy import Column, Integer, String, DateTime, Boolean, CheckConstraint
from datetime import datetime
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="ANALYST", nullable=False, index=True)
    clearance_level = Column(String, default="Alpha", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, nullable=True, index=True)
    password_reset_token = Column(String, nullable=True, index=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    lockout_until = Column(DateTime, nullable=True)
    current_refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("role IN ('ANALYST', 'EOC_LEAD', 'ADMINISTRATOR')", name="check_user_roles"),
        CheckConstraint("clearance_level IN ('Alpha', 'Beta', 'Omega')", name="check_clearance_levels"),
    )
