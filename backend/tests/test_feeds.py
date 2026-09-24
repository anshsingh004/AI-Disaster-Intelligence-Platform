import unittest
import os
import sys
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

# Ensure root path is configured for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app as fastapi_app
from app.services.feed_service import fetch_usgs_earthquakes, fetch_weather_telemetry
import app.models
from app.db import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


class TestPublicFeeds(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)
        fastapi_app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(fastapi_app)

    @classmethod
    def tearDownClass(cls):
        fastapi_app.dependency_overrides.clear()

    def test_01_parse_usgs_mock_feed(self):
        mock_geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "us7000test1",
                    "properties": {
                        "mag": 5.4,
                        "place": "12 km SSW of Hualien City, Taiwan",
                        "time": 1727218400000
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [121.60, 23.95, 18.5]
                    }
                },
                {
                    "type": "Feature",
                    "id": "us7000test2",
                    "properties": {
                        "mag": 2.1,  # Below threshold
                        "place": "Southern California",
                        "time": 1727218500000
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [-116.5, 33.2, 8.0]
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = unittest.mock.MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_geojson
            mock_get.return_value = mock_resp

            results = asyncio.run(fetch_usgs_earthquakes(min_magnitude=3.5))

            self.assertEqual(len(results), 1)
            event = results[0]
            self.assertEqual(event["disaster_type"], "earthquake")
            self.assertEqual(event["latitude"], 23.95)
            self.assertEqual(event["longitude"], 121.60)
            self.assertEqual(event["raw_telemetry"]["magnitude"], 5.4)
            self.assertEqual(event["source_origin"], "USGS")
            self.assertIn("Hualien City", event["title"])

    def test_02_usgs_timeout_graceful_recovery(self):
        import httpx
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("USGS timed out")):
            results = asyncio.run(fetch_usgs_earthquakes(min_magnitude=3.5))
            self.assertEqual(results, [])

    def test_03_weather_telemetry_fetch_and_fallback(self):
        mock_weather = {
            "current": {
                "time": "2026-09-24T22:00",
                "temperature_2m": 28.5,
                "relative_humidity_2m": 82.0,
                "precipitation": 12.4,
                "wind_speed_10m": 35.0
            }
        }
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = unittest.mock.MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_weather
            mock_get.return_value = mock_resp

            data = asyncio.run(fetch_weather_telemetry(19.07, 72.87))
            self.assertEqual(data["precipitation"], 12.4)
            self.assertEqual(data["wind_speed_10m"], 35.0)
            self.assertEqual(data["temperature_2m"], 28.5)

    def test_04_weather_timeout_fallback(self):
        import httpx
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Open-Meteo timeout")):
            data = asyncio.run(fetch_weather_telemetry(19.07, 72.87))
            self.assertEqual(data["precipitation"], 0.0)
            self.assertEqual(data["temperature_2m"], 20.0)

    def test_05_feeds_scan_endpoint_and_deduplication(self):
        mock_events = [
            {
                "external_id": "us_test_feed_999",
                "title": "M 5.8 - Offshore Northern California",
                "disaster_type": "earthquake",
                "latitude": 40.35,
                "longitude": -124.60,
                "raw_telemetry": {
                    "magnitude": 5.8,
                    "depth_km": 10.0,
                    "place": "Offshore Northern California",
                    "time": 1727218600000,
                    "seismic_magnitude": 5.8
                },
                "source_origin": "USGS"
            }
        ]

        with patch("app.routers.feeds.fetch_usgs_earthquakes", return_value=mock_events), \
             patch("app.routers.feeds.fetch_weather_telemetry", return_value={"precipitation": 0.0, "wind_speed_10m": 15.0}):

            # First scan request: creates disaster
            response1 = self.client.post("/api/v1/feeds/scan?min_magnitude=3.0")
            self.assertEqual(response1.status_code, 200)
            data1 = response1.json()["data"]

            self.assertEqual(data1["scanned"], 1)
            self.assertEqual(data1["new_ingested"], 1)
            self.assertEqual(len(data1["events"]), 1)
            self.assertEqual(data1["events"][0]["title"], "M 5.8 - Offshore Northern California")
            self.assertEqual(data1["events"][0]["source_origin"], "USGS")
            self.assertIsNotNone(data1["events"][0]["sitrep_summary"])

            # Second scan request: deduplication prevents re-ingestion
            response2 = self.client.post("/api/v1/feeds/scan?min_magnitude=3.0")
            self.assertEqual(response2.status_code, 200)
            data2 = response2.json()["data"]

            self.assertEqual(data2["scanned"], 1)
            self.assertEqual(data2["new_ingested"], 0)
            self.assertEqual(len(data2["events"]), 0)

    def test_06_live_weather_endpoint(self):
        with patch("app.routers.feeds.fetch_weather_telemetry", return_value={"temperature_2m": 22.0, "precipitation": 0.0, "wind_speed_10m": 10.0}):
            response = self.client.get("/api/v1/feeds/weather?lat=37.77&lon=-122.41")
            self.assertEqual(response.status_code, 200)
            data = response.json()["data"]
            self.assertEqual(data["temperature_2m"], 22.0)


if __name__ == "__main__":
    unittest.main()
