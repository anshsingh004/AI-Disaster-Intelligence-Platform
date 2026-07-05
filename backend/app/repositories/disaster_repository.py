from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.disaster import Disaster
from app.schemas.disaster import DisasterInput, DisasterOutput

class DisasterRepository(BaseRepository):
    """Repository class encapsulating all data-access calls on the disasters table."""

    def get_all(self) -> List[Disaster]:
        """Fetch all disaster records ordered by creation timestamp descending."""
        return self.db.query(Disaster).order_by(Disaster.created_at.desc()).all()

    def get_by_id(self, disaster_id: int) -> Optional[Disaster]:
        """Retrieve a specific disaster record by its ID."""
        return self.db.query(Disaster).filter(Disaster.id == disaster_id).first()

    def create(self, data: DisasterInput, result: DisasterOutput) -> Disaster:
        """Create and persist a new disaster record."""
        db_disaster = Disaster(
            disaster_type=result.disaster_type,
            severity_score=result.severity_score,
            risk_level=result.risk_level,
            population_at_risk=result.population_at_risk,
            confidence=result.confidence,
            latitude=data.latitude,
            longitude=data.longitude,
            created_at=result.timestamp
        )
        self.db.add(db_disaster)
        self.db.commit()
        self.db.refresh(db_disaster)
        return db_disaster
