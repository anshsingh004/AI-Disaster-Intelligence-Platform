from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app.repositories.base import BaseRepository
from app.models.disaster import Disaster
from app.schemas.disaster import DisasterInput, DisasterOutput

class DisasterRepository(BaseRepository):
    """Repository class encapsulating all data-access calls on the disasters table."""

    def get_all(self) -> List[Disaster]:
        """Fetch all disaster records ordered by creation timestamp descending. (Backward compatible)."""
        return self.db.query(Disaster).order_by(Disaster.created_at.desc()).all()

    def get_paginated(
        self,
        page: int = 1,
        limit: int = 10,
        disaster_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        min_severity: Optional[float] = None,
        max_severity: Optional[float] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        search: Optional[str] = None
    ) -> Tuple[List[Disaster], int]:
        """Queries disasters dynamically applying pagination, sorting, filters, and searches."""
        query = self.db.query(Disaster)

        # 1. Apply Categorical Filters
        if disaster_type:
            query = query.filter(Disaster.disaster_type == disaster_type)
        if risk_level:
            query = query.filter(Disaster.risk_level == risk_level)
            
        # 2. Apply Numerical Range Checks
        if min_severity is not None:
            query = query.filter(Disaster.severity_score >= min_severity)
        if max_severity is not None:
            query = query.filter(Disaster.severity_score <= max_severity)

        # 3. Apply Text Wildcard Search
        if search:
            query = query.filter(Disaster.disaster_type.ilike(f"%{search}%"))

        # 4. Count total matched documents
        total = query.count()

        # 5. Apply Dynamic Column Sorting
        sort_col = getattr(Disaster, sort_by, None)
        if sort_col is None:
            sort_col = Disaster.created_at  # Fallback sorting column

        if order.lower() == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        # 6. Apply pagination slices
        offset = (page - 1) * limit
        items = query.limit(limit).offset(offset).all()

        return items, total

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
