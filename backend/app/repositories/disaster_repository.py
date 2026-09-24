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
            query = query.filter(
                (Disaster.disaster_type.ilike(f"%{search}%")) |
                (Disaster.title.ilike(f"%{search}%"))
            )

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
        """Create and persist a new disaster record with streamlined operational fields."""
        raw_telemetry = data.raw_telemetry or {
            "rainfall": data.weather_rainfall,
            "wind_speed": data.weather_wind_speed,
            "social_score": data.social_signal_score,
        }
        title = data.title or result.title or f"{result.disaster_type.capitalize()} Incident"

        db_disaster = Disaster(
            title=title,
            disaster_type=result.disaster_type,
            risk_level=result.risk_level,
            latitude=data.latitude,
            longitude=data.longitude,
            raw_telemetry=raw_telemetry,
            sitrep_summary=result.sitrep_summary,
            recommended_actions=result.recommended_actions,
            source_origin=data.source_origin or "MANUAL",
            acknowledged=False,
            # Backwards compatibility values
            severity_score=result.severity_score,
            population_at_risk=result.population_at_risk,
            confidence=result.confidence,
            created_at=result.timestamp,
        )
        self.db.add(db_disaster)
        self.db.commit()
        self.db.refresh(db_disaster)

        # Create linked alert for the newly logged disaster
        from app.models.alert import Alert
        alert_title = f"{db_disaster.risk_level} Alert: {db_disaster.disaster_type.capitalize()} Detected"
        severity_val = result.severity_score if result.severity_score is not None else 0.6
        alert_description = (
            f"Threat evaluation identified {db_disaster.disaster_type} risk at coordinates "
            f"{db_disaster.latitude:.4f}, {db_disaster.longitude:.4f}."
        )

        db_alert = Alert(
            disaster_id=db_disaster.id,
            level=db_disaster.risk_level,
            title=alert_title,
            description=alert_description,
            escalation_probability=round(severity_val * 100.0, 1),
            acknowledged=False,
            created_at=db_disaster.created_at,
        )
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_disaster)

        return db_disaster
