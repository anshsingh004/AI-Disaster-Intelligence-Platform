from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.repositories.base import BaseRepository
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserRepository(BaseRepository):
    """Repository class encapsulating all data-access operations on user-related tables."""

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user record by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_verification_token(self, token: str) -> Optional[User]:
        """Fetch a user record matching a specific verification token."""
        return self.db.query(User).filter(User.verification_token == token).first()

    def get_by_reset_token(self, token: str) -> Optional[User]:
        """Fetch a user record matching a specific password reset token."""
        return self.db.query(User).filter(User.password_reset_token == token).first()

    def create(self, data: UserCreate) -> User:
        """Create, hash, and persist a new user account."""
        hashed_pw = get_password_hash(data.password)
        db_user = User(
            name=data.name,
            email=data.email,
            hashed_password=hashed_pw,
            role=data.role or "ANALYST",
            clearance_level=data.clearance_level or "Alpha",
            is_active=True,
            is_verified=False
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, user: User) -> User:
        """Commit changes to a user record and refresh."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def increment_failed_attempts(self, user: User) -> User:
        """Increments failed login counter."""
        user.failed_login_attempts += 1
        return self.update(user)

    def reset_failed_attempts(self, user: User) -> User:
        """Resets failed login counter and clear lockout states."""
        user.failed_login_attempts = 0
        user.lockout_until = None
        return self.update(user)

    def lock_account(self, user: User, minutes: int = 15) -> User:
        """Locks user account for a specified time period."""
        user.lockout_until = datetime.utcnow() + timedelta(minutes=minutes)
        return self.update(user)

    def log_security_event(self, email: str, action: str, ip: str) -> None:
        """Records a security action to the audit logs."""
        log = AuditLog(
            user_email=email,
            action=action,
            ip_address=ip
        )
        self.db.add(log)
        self.db.commit()
