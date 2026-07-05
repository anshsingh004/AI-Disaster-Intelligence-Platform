import hashlib
import json
from datetime import datetime, timezone
from app.schemas.disaster import DisasterInput, DisasterOutput
from app.services.ai.factory import AIFactory
from app.services.ai.caching import prediction_cache
from app.services.ai.onnx_layer import execute_with_retry

def run_disaster_inference(data: DisasterInput) -> DisasterOutput:
    """Processes disaster indicators by running them through cache layers and specific model stubs."""
    # 1. Generate cache key to optimize latency
    cache_payload = {
        "lat": data.latitude,
        "lng": data.longitude,
        "rainfall": data.weather_rainfall,
        "wind": data.weather_wind_speed,
        "social": data.social_signal_score
    }
    cache_key = hashlib.md5(json.dumps(cache_payload, sort_keys=True).encode("utf-8")).hexdigest()

    # 2. Check prediction cache
    cached_result = prediction_cache.get(cache_key)
    if cached_result:
        return DisasterOutput(
            disaster_type=cached_result["disaster_type"],
            severity_score=cached_result["severity_score"],
            risk_level=cached_result["risk_level"],
            population_at_risk=cached_result["population_at_risk"],
            confidence=cached_result["confidence"],
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
        )

    # 3. Format inputs for models
    weather_input = {"rainfall": data.weather_rainfall, "wind_speed": data.weather_wind_speed}
    nlp_input = {
        "text": f"Alert! Extreme weather signals detected at coordinates {data.latitude}, {data.longitude}. "
                f"Social threat score: {data.social_signal_score}"
    }
    satellite_input = {
        "water_signature": 0.8 if data.weather_rainfall > 120 else 0.1,
        "bbox": [data.latitude - 0.1, data.longitude - 0.1, data.latitude + 0.1, data.longitude + 0.1]
    }

    # 4. Execute queries using the independent AI Service Layer factories wrapped in retries
    weather_pred = execute_with_retry(AIFactory.get_weather_model().predict, weather_input)
    nlp_pred = execute_with_retry(AIFactory.get_tweet_model().predict, nlp_input)
    satellite_pred = execute_with_retry(AIFactory.get_satellite_model().predict, satellite_input)

    # 5. Core correlation logic matching the original baseline proxy rules
    disaster_type = "none"
    severity_score = 0.2
    risk_level = "LOW"
    population_at_risk = 10000
    confidence = 0.6

    if data.weather_rainfall > 120 and data.social_signal_score > 0.75:
        disaster_type = "flood"
        severity_score = round(min(1.0, data.weather_rainfall / 200), 2)
        risk_level = "HIGH"
        population_at_risk = 150000
        confidence = 0.9
    elif data.weather_wind_speed > 45 and data.social_signal_score > 0.6:
        disaster_type = "fire"
        severity_score = round(min(1.0, data.weather_wind_speed / 80), 2)
        risk_level = "MEDIUM"
        population_at_risk = 60000
        confidence = 0.85
    elif data.social_signal_score > 0.65:
        disaster_type = "earthquake"
        severity_score = 0.7
        risk_level = "MEDIUM"
        population_at_risk = 80000
        confidence = 0.8

    result_dict = {
        "disaster_type": disaster_type,
        "severity_score": severity_score,
        "risk_level": risk_level,
        "population_at_risk": population_at_risk,
        "confidence": confidence
    }

    # 6. Save result to cache
    prediction_cache.set(cache_key, result_dict)

    return DisasterOutput(
        disaster_type=disaster_type,
        severity_score=severity_score,
        risk_level=risk_level,
        population_at_risk=population_at_risk,
        confidence=confidence,
        timestamp=datetime.now(timezone.utc).replace(tzinfo=None)
    )
