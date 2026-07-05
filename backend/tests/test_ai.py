import unittest
import os
import sys
from datetime import datetime, timezone

# Ensure root path is configured for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.schemas.disaster import DisasterInput
from app.services.ml_service import run_disaster_inference
from app.services.ai.factory import AIFactory
from app.services.ai.caching import prediction_cache
from app.services.ai.onnx_layer import execute_with_retry

class TestAIServiceLayer(unittest.TestCase):
    def setUp(self):
        prediction_cache.clear()

    def test_01_model_loading_and_lazy_load(self):
        # Retrieve satellite model from factory
        satellite = AIFactory.get_satellite_model()
        self.assertFalse(satellite.is_loaded)
        
        # Ensure lazy loading activates on predict
        input_data = {"water_signature": 0.8, "bbox": [12.0, 13.0, 14.0, 15.0]}
        res = satellite.predict(input_data)
        
        self.assertTrue(satellite.is_loaded)
        self.assertEqual(res["classification"], "flooded_area")
        self.assertEqual(res["confidence"], 0.92)

    def test_02_satellite_request_batching(self):
        satellite = AIFactory.get_satellite_model()
        batch_inputs = [
            {"water_signature": 0.8, "bbox": [10.0, 20.0, 11.0, 21.0]},
            {"water_signature": 0.1, "bbox": [30.0, 40.0, 31.0, 41.0]},
            {"thermal_signature": 0.9, "bbox": [50.0, 60.0, 51.0, 61.0]}
        ]
        results = satellite.predict_batch(batch_inputs)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["classification"], "flooded_area")
        self.assertEqual(results[1]["classification"], "clear")
        self.assertEqual(results[2]["classification"], "burn_scar")

    def test_03_inference_cache(self):
        payload = DisasterInput(
            latitude=28.6139,
            longitude=77.209,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=150.0,
            weather_wind_speed=20.0,
            social_signal_score=0.85
        )
        
        # 1. First execution: populates cache
        res1 = run_disaster_inference(payload)
        self.assertEqual(res1.disaster_type, "flood")
        
        # Manually alter cache entry to verify consecutive requests hit cache
        cache_key = list(prediction_cache.cache.keys())[0]
        prediction_cache.set(cache_key, {
            "disaster_type": "cached_earthquake",
            "severity_score": 0.9,
            "risk_level": "CRITICAL",
            "population_at_risk": 50000,
            "confidence": 0.95
        })
        
        # 2. Second execution: retrieves modified cache values
        res2 = run_disaster_inference(payload)
        self.assertEqual(res2.disaster_type, "cached_earthquake")

    def test_04_retry_logic_recovery(self):
        calls = 0
        
        def failing_function(threshold):
            nonlocal calls
            calls += 1
            if calls < threshold:
                raise ValueError("Temporary hardware exception")
            return "Inference Success"

        # Mocking retry configurations temporarily
        from app.services.ai.config import ai_settings
        original_retries = ai_settings.INFERENCE_MAX_RETRIES
        ai_settings.INFERENCE_MAX_RETRIES = 3
        ai_settings.INFERENCE_RETRY_BACKOFF = 0.1 # fast retries for tests
        
        try:
            # Recovers on 2nd retry
            res = execute_with_retry(failing_function, threshold=2)
            self.assertEqual(res, "Inference Success")
            self.assertEqual(calls, 2)
            
            # Fails after max retries
            calls = 0
            with self.assertRaises(ValueError):
                execute_with_retry(failing_function, threshold=5)
        finally:
            ai_settings.INFERENCE_MAX_RETRIES = original_retries
            
    def test_05_predict_baseline_correlation(self):
        # 1. Test Flood Trigger
        res = run_disaster_inference(DisasterInput(
            latitude=1.0, longitude=1.0,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=130.0, weather_wind_speed=10.0, social_signal_score=0.8
        ))
        self.assertEqual(res.disaster_type, "flood")
        self.assertEqual(res.risk_level, "HIGH")

        # 2. Test Fire Trigger
        res = run_disaster_inference(DisasterInput(
            latitude=1.0, longitude=1.0,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=20.0, weather_wind_speed=50.0, social_signal_score=0.7
        ))
        self.assertEqual(res.disaster_type, "fire")
        self.assertEqual(res.risk_level, "MEDIUM")

        # 3. Test Earthquake Trigger
        res = run_disaster_inference(DisasterInput(
            latitude=1.0, longitude=1.0,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=10.0, weather_wind_speed=10.0, social_signal_score=0.7
        ))
        self.assertEqual(res.disaster_type, "earthquake")
        
        # 4. Test Low Risk Trigger
        res = run_disaster_inference(DisasterInput(
            latitude=1.0, longitude=1.0,
            timestamp=datetime.now(timezone.utc),
            weather_rainfall=5.0, weather_wind_speed=5.0, social_signal_score=0.2
        ))
        self.assertEqual(res.disaster_type, "none")
