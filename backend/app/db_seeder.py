import os
import sys
import logging
from datetime import datetime

# Ensure backend root is on sys.path when executed directly as a script
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.db import db_session
from app.models.disaster import Disaster
from app.models.alert import Alert
from app.models.report import Report
from app.models.user import User
from app.models.knowledge import KnowledgeBase
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def seed_database():
    """Populates the database with initial operational dataset if empty."""
    with db_session() as db:
        # 1. Seed Operational Users
        logger.info("Verifying operational users...")
        analyst = db.query(User).filter(User.email == "analyst@terra-aura.dev").first()
        if not analyst:
            logger.info("Seeding primary analyst user: analyst@terra-aura.dev / Analyst@2026")
            analyst = User(
                name="Primary Analyst",
                email="analyst@terra-aura.dev",
                hashed_password=get_password_hash("Analyst@2026"),
                role="ANALYST",
                clearance_level="Alpha",
                is_active=True,
                is_verified=True,
            )
            db.add(analyst)
        else:
            analyst.hashed_password = get_password_hash("Analyst@2026")
            analyst.is_active = True
            analyst.is_verified = True
            analyst.failed_login_attempts = 0
            analyst.lockout_until = None

        commander = db.query(User).filter(User.email == "commander@terra-aura.dev").first()
        if not commander:
            logger.info("Seeding commander user: commander@terra-aura.dev / Commander@2026")
            commander = User(
                name="Commander",
                email="commander@terra-aura.dev",
                hashed_password=get_password_hash("Commander@2026"),
                role="ADMINISTRATOR",
                clearance_level="Omega",
                is_active=True,
                is_verified=True,
            )
            db.add(commander)
        else:
            commander.hashed_password = get_password_hash("Commander@2026")
            commander.is_active = True
            commander.is_verified = True
            commander.failed_login_attempts = 0
            commander.lockout_until = None
        db.flush()

        # 2. Seed KnowledgeBase for RAG if empty
        kb_count = db.query(KnowledgeBase).count()
        if kb_count == 0:
            logger.info("Seeding initial KnowledgeBase RAG manuals...")
            kb1 = KnowledgeBase(
                title="Wildfire Rapid Containment Standard Operating Procedure",
                category="SOP",
                content=(
                    "When fire propagation probability exceeds 80% under high-wind conditions (>40 km/h), "
                    "incident command must immediately establish a 5km primary containment perimeter. Aerial "
                    "water/retardant drops should target advancing flanks while ground crews secure structures."
                ),
                source_url="https://terra-aura.org/sop/wildfire-containment-v1",
            )
            kb2 = KnowledgeBase(
                title="Urban Flood Plain Evacuation Protocol & Watershed Triage",
                category="Evacuation",
                content=(
                    "Inundation depths surpassing 0.5 meters in residential corridors necessitate immediate Level 1 "
                    "evacuation. First responders must pre-position high-water rescue craft at designated grid muster "
                    "stations and redirect regional power distribution through elevated sub-stations."
                ),
                source_url="https://terra-aura.org/sop/urban-flood-triage-v2",
            )
            kb3 = KnowledgeBase(
                title="Post-Seismic Infrastructure Assessment & Secondary Hazard Mitigation",
                category="Structural",
                content=(
                    "Following structural tremors exceeding 5.0 magnitude, teams must verify natural gas trunk line "
                    "pressures, examine primary bridge abutments, and isolate potential landslide slopes before "
                    "clearing evacuation routes for civilian traffic."
                ),
                source_url="https://terra-aura.org/sop/seismic-inspection-v1",
            )
            db.add_all([kb1, kb2, kb3])
            db.flush()

        # 3. Seed Disasters if table empty
        disaster_count = db.query(Disaster).count()
        if disaster_count > 0:
            logger.info("Database disasters already populated. Skipping incident seeding.")
            return

        logger.info("Seeding database with default disaster operational logs...")

        d1 = Disaster(
            title="Northern Ridge Wildfire Flare",
            disaster_type="fire",
            risk_level="CRITICAL",
            latitude=28.6139,
            longitude=77.209,
            raw_telemetry={"rainfall": 0.0, "wind_speed": 62.0, "thermal_index": 94},
            sitrep_summary="High-velocity thermal expansion detected across northern forestry ridge.",
            recommended_actions=["Deploy aerial suppression", "Evacuate northern ridge zones within 5km"],
            source_origin="EOC_TELEMETRY",
            acknowledged=False,
            severity_score=0.94,
            population_at_risk=150000,
            confidence=0.90,
            created_at=datetime.utcnow(),
        )
        d2 = Disaster(
            title="River Delta B7 Flash Flood Surge",
            disaster_type="flood",
            risk_level="HIGH",
            latitude=19.076,
            longitude=72.8777,
            raw_telemetry={"rainfall": 180.0, "wind_speed": 22.0, "water_level_m": 3.8},
            sitrep_summary="Sustained precipitation upstream combined with compromised levee infrastructure.",
            recommended_actions=["Inspect levee gates", "Issue voluntary evacuation for basin B7"],
            source_origin="SENSOR_METEO",
            acknowledged=True,
            severity_score=0.72,
            population_at_risk=60000,
            confidence=0.85,
            created_at=datetime.utcnow(),
        )
        d3 = Disaster(
            title="Tokyo Metropolitan Seismic Tremor",
            disaster_type="earthquake",
            risk_level="MEDIUM",
            latitude=35.6895,
            longitude=139.6917,
            raw_telemetry={"magnitude": 4.8, "depth_km": 12.0, "social_cluster_score": 0.72},
            sitrep_summary="Moderate ground acceleration recorded with localized utility disruptions.",
            recommended_actions=["Inspect gas lines", "Verify transport line integrity"],
            source_origin="SEISMIC_NETWORK",
            acknowledged=True,
            severity_score=0.51,
            population_at_risk=80000,
            confidence=0.80,
            created_at=datetime.utcnow(),
        )

        db.add_all([d1, d2, d3])
        db.flush()

        # 4. Seed Alerts
        a1 = Alert(
            disaster_id=d1.id,
            level="CRITICAL",
            title="Unidentified Thermal Signature, Sector 4",
            description="Predictive models indicate a 94% probability of rapid expansion. Atmospheric conditions favor escalation.",
            escalation_probability=87.0,
            acknowledged=False,
            created_at=d1.created_at,
        )
        a2 = Alert(
            disaster_id=d2.id,
            level="HIGH",
            title="Flood Risk Escalation, River Delta B7",
            description="Sustained rainfall upstream combined with compromised levee infrastructure.",
            escalation_probability=72.0,
            acknowledged=True,
            created_at=d2.created_at,
        )

        db.add_all([a1, a2])

        # 5. Seed Reports
        r1 = Report(
            disaster_id=d1.id,
            report_code="RPT-8492",
            type="Wildfire",
            risk="critical",
            location="Sector 7G, Northern Ridge",
            status="active",
            summary="Emergency drone reconnaissance assessment report.",
            created_at=d1.created_at,
        )
        r2 = Report(
            disaster_id=d2.id,
            report_code="RPT-8491",
            type="Flood Warning",
            risk="high",
            location="River Valley Delta",
            status="monitoring",
            summary="Basin-level watershed accumulation and stress report.",
            created_at=d2.created_at,
        )

        db.add_all([r1, r2])
        db.commit()
        logger.info("Database seeding successfully completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()

