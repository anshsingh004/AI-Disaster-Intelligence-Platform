import unittest
import os
import sys
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Ensure root path is configured for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app as fastapi_app
from app.services.llm_service import (
    deterministic_fallback_sitrep,
    generate_incident_sitrep,
    generate_incident_sitrep_sync
)
import app.models
from app.db import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup test in-memory database with StaticPool so all threads share tables
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestLLMServiceAndFallback(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)
        fastapi_app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(fastapi_app)

    @classmethod
    def tearDownClass(cls):
        fastapi_app.dependency_overrides.clear()

    def test_01_deterministic_critical_fallback(self):
        telemetry = {"rainfall": 85.0, "wind_speed": 40.0}
        sitrep = deterministic_fallback_sitrep(telemetry, "flood")

        self.assertEqual(sitrep["risk_level"], "CRITICAL")
        self.assertIn("mandatory evacuation", sitrep["recommended_actions"][0].lower())
        self.assertIn("Deterministic Operational Rules Engine", sitrep["ai_confidence_note"])
        self.assertIn("executive_summary", sitrep)
        self.assertIn("situation_analysis", sitrep)
        self.assertIn("infrastructure_impact", sitrep)

    def test_02_deterministic_high_fallback(self):
        telemetry = {"rainfall": 45.0, "wind_speed": 50.0}
        sitrep = deterministic_fallback_sitrep(telemetry, "flood")

        self.assertEqual(sitrep["risk_level"], "HIGH")
        self.assertIn("emergency warning alerts", sitrep["recommended_actions"][0].lower())

    def test_03_deterministic_medium_fallback(self):
        telemetry = {"rainfall": 20.0, "wind_speed": 45.0}
        sitrep = deterministic_fallback_sitrep(telemetry, "storm")

        self.assertEqual(sitrep["risk_level"], "MEDIUM")
        self.assertIn("localized waterlogging", sitrep["recommended_actions"][0].lower())

    def test_04_deterministic_low_fallback(self):
        telemetry = {"rainfall": 2.0, "wind_speed": 5.0}
        sitrep = deterministic_fallback_sitrep(telemetry, "monitoring")

        self.assertEqual(sitrep["risk_level"], "LOW")
        self.assertIn("sensor telemetry polling", sitrep["recommended_actions"][0].lower())

    def test_05_generate_sitrep_without_api_key(self):
        # Ensure GEMINI_API_KEY is not set
        with patch.dict(os.environ, {}, clear=True):
            sitrep = asyncio.run(generate_incident_sitrep(
                telemetry_data={"rainfall": 80.0},
                incident_type="flood"
            ))
            self.assertEqual(sitrep["risk_level"], "CRITICAL")
            self.assertIn("Deterministic Operational Rules Engine", sitrep["ai_confidence_note"])

    def test_06_generate_sitrep_with_invalid_key_does_not_throw(self):
        # Invalid API key must gracefully execute deterministic fallback without raising
        with patch.dict(os.environ, {"GEMINI_API_KEY": "AIzaNotAValidKey1234567890"}):
            sitrep = asyncio.run(generate_incident_sitrep(
                telemetry_data={"rainfall": 10.0, "wind_speed": 10.0},
                incident_type="flood"
            ))
            self.assertIsNotNone(sitrep)
            self.assertIn(sitrep["risk_level"], ("LOW", "MEDIUM", "HIGH", "CRITICAL"))
            self.assertIn("executive_summary", sitrep)
            self.assertIn("recommended_actions", sitrep)

    def test_07_generate_sitrep_timeout_fallback(self):
        # Simulate timeout in Gemini client
        with patch("app.services.llm_service.get_genai_client") as mock_get_client:
            mock_client = AsyncMock()
            # simulate a call that times out
            async def hang_forever(*args, **kwargs):
                await asyncio.sleep(10)
            mock_client.aio.models.generate_content = hang_forever
            mock_get_client.return_value = mock_client

            sitrep = asyncio.run(generate_incident_sitrep(
                telemetry_data={"rainfall": 90.0},
                incident_type="flood"
            ))
            self.assertEqual(sitrep["risk_level"], "CRITICAL")
            self.assertIn("Deterministic Operational Rules Engine", sitrep["ai_confidence_note"])

    def test_08_sync_wrapper_fallback(self):
        sitrep = generate_incident_sitrep_sync(
            telemetry_data={"rainfall": 50.0},
            incident_type="flood"
        )
        self.assertEqual(sitrep["risk_level"], "HIGH")
        self.assertIsInstance(sitrep["recommended_actions"], list)

    def test_09_api_predict_endpoint_resilience(self):
        # Test POST /api/v1/predict/disaster returns 201 with populated SITREP even with no GEMINI_API_KEY
        payload = {
            "title": "Severe Coastal Inundation",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "weather_rainfall": 95.0,
            "weather_wind_speed": 45.0,
            "social_signal_score": 0.85
        }
        response = self.client.post("/api/v1/predict/disaster", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]

        self.assertEqual(data["title"], "Severe Coastal Inundation")
        self.assertEqual(data["risk_level"], "CRITICAL")
        self.assertIsNotNone(data["sitrep_summary"])
        self.assertIsInstance(data["recommended_actions"], list)
        self.assertGreater(len(data["recommended_actions"]), 0)

    def test_10_api_disasters_endpoint_alias(self):
        # Test POST /api/v1/disasters alias returns 201
        payload = {
            "title": "Moderate Tremor Detection",
            "latitude": 34.0522,
            "longitude": -118.2437,
            "weather_rainfall": 5.0,
            "weather_wind_speed": 10.0,
            "social_signal_score": 0.72
        }
        response = self.client.post("/api/v1/disasters", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]

        self.assertIsNotNone(data["id"])
        self.assertIsNotNone(data["sitrep_summary"])


if __name__ == "__main__":
    unittest.main()
