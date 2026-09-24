import unittest
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure root path is configured for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.disaster import DisasterInput
from app.services.ml_service import run_disaster_inference, prediction_cache
from app.db import Base
from app.models.disaster import Disaster
from app.models.knowledge import KnowledgeBase
from app.repositories.disaster_repository import DisasterRepository
from app.services.report_service import generate_report_content


class TestInferenceAndStreamlinedModels(unittest.TestCase):
    def setUp(self):
        prediction_cache.clear()
        # In-memory SQLite for testing repository and models
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()
        self.repo = DisasterRepository(self.db)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_01_predict_baseline_correlation(self):
        # 1. Flood Trigger
        res = run_disaster_inference(DisasterInput(
            title="Monsoon Flooding",
            latitude=19.076, longitude=72.877,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=140.0, weather_wind_speed=15.0, social_signal_score=0.85
        ))
        self.assertEqual(res.disaster_type, "flood")
        self.assertIn(res.risk_level, ("HIGH", "CRITICAL"))

        # 2. Fire Trigger
        res = run_disaster_inference(DisasterInput(
            title="Forest Fire Incident",
            latitude=34.052, longitude=-118.243,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=10.0, weather_wind_speed=55.0, social_signal_score=0.75
        ))
        self.assertEqual(res.disaster_type, "fire")
        self.assertIn(res.risk_level, ("MEDIUM", "HIGH"))

        # 3. Earthquake Trigger
        res = run_disaster_inference(DisasterInput(
            title="Seismic Tremor",
            latitude=37.774, longitude=-122.419,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=5.0, weather_wind_speed=10.0, social_signal_score=0.72
        ))
        self.assertEqual(res.disaster_type, "earthquake")

        # 4. Low Risk Baseline
        res = run_disaster_inference(DisasterInput(
            title="Calm Conditions",
            latitude=0.0, longitude=0.0,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=2.0, weather_wind_speed=5.0, social_signal_score=0.1
        ))
        self.assertEqual(res.disaster_type, "none")
        self.assertEqual(res.risk_level, "LOW")

    def test_02_inference_cache(self):
        payload = DisasterInput(
            title="Coastal Flash Flood",
            latitude=28.6139,
            longitude=77.209,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=150.0,
            weather_wind_speed=20.0,
            social_signal_score=0.85
        )

        # 1. First execution populates cache
        res1 = run_disaster_inference(payload)
        self.assertEqual(res1.disaster_type, "flood")

        # 2. Manually mutate cache entry
        cache_key = list(prediction_cache._cache.keys())[0]
        prediction_cache.set(cache_key, {
            "title": "Mutated Cache Incident",
            "disaster_type": "cached_earthquake",
            "severity_score": 0.9,
            "risk_level": "CRITICAL",
            "population_at_risk": 50000,
            "confidence": 0.95
        })

        # 3. Second execution returns mutated cache
        res2 = run_disaster_inference(payload)
        self.assertEqual(res2.disaster_type, "cached_earthquake")

    def test_03_disaster_model_with_new_fields(self):
        input_data = DisasterInput(
            title="North District Flood Inundation",
            latitude=25.5941,
            longitude=85.1376,
            weather_rainfall=120.0,
            weather_wind_speed=15.0,
            social_signal_score=0.8,
            source_origin="SENSOR_NETWORK"
        )
        prediction = run_disaster_inference(input_data)
        record = self.repo.create(input_data, prediction)

        self.assertIsNotNone(record.id)
        self.assertEqual(record.title, "North District Flood Inundation")
        self.assertEqual(record.source_origin, "SENSOR_NETWORK")
        self.assertFalse(record.acknowledged)
        self.assertIsInstance(record.raw_telemetry, dict)
        self.assertIn("rainfall", record.raw_telemetry)

        # Acknowledge incident
        record.acknowledged = True
        self.db.commit()
        self.db.refresh(record)
        self.assertTrue(record.acknowledged)

    def test_04_knowledge_base_crud(self):
        doc = KnowledgeBase(
            title="Flood Evacuation Standard Operating Procedure",
            category="SOP",
            content="Immediate deployment of motorized rescue boats along low-lying riverbanks.",
            source_url="https://eoc.internal/sop/flood-01"
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.category, "SOP")
        self.assertIsNotNone(doc.created_at)

        # Query filter test
        fetched = self.db.query(KnowledgeBase).filter(KnowledgeBase.category == "SOP").first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "Flood Evacuation Standard Operating Procedure")

    def test_05_report_service_with_nullable_fields(self):
        # Verify that generating report content works even when legacy ML fields are None
        disaster = Disaster(
            title="Telemetry-Only Incident",
            disaster_type="flood",
            risk_level="HIGH",
            latitude=13.0827,
            longitude=80.2707,
            severity_score=None,
            confidence=None,
            population_at_risk=None,
            raw_telemetry={"rainfall_mm": 110.0}
        )
        self.db.add(disaster)
        self.db.commit()
        self.db.refresh(disaster)

        content = generate_report_content(disaster)
        self.assertIn("executive_summary", content)
        self.assertIn("risk_assessment", content)
        self.assertIn("recommended_actions", content)


if __name__ == "__main__":
    unittest.main()
