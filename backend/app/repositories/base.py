from sqlalchemy.orm import Session

class BaseRepository:
    """Base class for all repository instances managing database operations."""
    def __init__(self, db: Session):
        self.db = db
