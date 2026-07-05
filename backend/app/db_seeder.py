import logging
from datetime import datetime
from app.db import db_session
from app.models.disaster import Disaster
from app.models.alert import Alert
from app.models.report import Report

logger = logging.getLogger(__name__)

def seed_database():
    """Populates the database with initial operational dataset if empty."""
    with db_session() as db:
        disaster_count = db.query(Disaster).count()
        if disaster_count > 0:
            logger.info("Database already populated. Skipping database seeding.")
            return

        logger.info("Seeding database with default disaster operational logs...")

        # 1. Seed Disasters
        d1 = Disaster(
            disaster_type="fire",
            severity_score=0.94,
            risk_level="CRITICAL",
            population_at_risk=150000,
            confidence=0.90,
            latitude=28.6139,
            longitude=77.209,
            created_at=datetime.utcnow()
        )
        d2 = Disaster(
            disaster_type="flood",
            severity_score=0.72,
            risk_level="HIGH",
            population_at_risk=60000,
            confidence=0.85,
            latitude=19.076,
            longitude=72.8777,
            created_at=datetime.utcnow()
        )
        d3 = Disaster(
            disaster_type="earthquake",
            severity_score=0.51,
            risk_level="MEDIUM",
            population_at_risk=80000,
            confidence=0.80,
            latitude=35.6895,
            longitude=139.6917,
            created_at=datetime.utcnow()
        )

        db.add_all([d1, d2, d3])
        db.flush()  # Flushes to obtain IDs for referencing in alerts and reports

        # 2. Seed Alerts
        a1 = Alert(
            disaster_id=d1.id,
            level="CRITICAL",
            title="Unidentified Thermal Signature, Sector 4",
            description="Predictive models indicate a 94% probability of rapid expansion. Atmospheric conditions favor escalation.",
            escalation_probability=87.0,
            acknowledged=False
        )
        a2 = Alert(
            disaster_id=d2.id,
            level="HIGH",
            title="Flood Risk Escalation, River Delta B7",
            description="Sustained rainfall upstream combined with compromised levee infrastructure.",
            escalation_probability=72.0,
            acknowledged=True
        )

        db.add_all([a1, a2])

        # 3. Seed Reports
        r1 = Report(
            disaster_id=d1.id,
            report_code="RPT-8492",
            type="Wildfire",
            risk="critical",
            location="Sector 7G, Northern Ridge",
            status="active",
            summary="Emergency drone reconnaissance assessment report."
        )
        r2 = Report(
            disaster_id=d2.id,
            report_code="RPT-8491",
            type="Flood Warning",
            risk="high",
            location="River Valley Delta",
            status="monitoring",
            summary="Basin-level watershed accumulation and stress report."
        )

        db.add_all([r1, r2])
        logger.info("Database seeding successfully completed.")
