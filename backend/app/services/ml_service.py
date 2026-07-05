from datetime import datetime
from app.schemas.disaster import DisasterInput, DisasterOutput
from ml.inference.predict import run_inference

def run_disaster_inference(data: DisasterInput) -> DisasterOutput:
    # Format request payload for model proxy
    input_dict = {
        "latitude": data.latitude,
        "longitude": data.longitude,
        "timestamp": data.timestamp.isoformat() if data.timestamp else datetime.utcnow().isoformat(),
        "weather_rainfall": data.weather_rainfall,
        "weather_wind_speed": data.weather_wind_speed,
        "social_signal_score": data.social_signal_score
    }
    
    # Execute inference
    prediction = run_inference(input_dict)
    
    return DisasterOutput(
        disaster_type=prediction["disaster_type"],
        severity_score=prediction["severity_score"],
        risk_level=prediction["risk_level"],
        population_at_risk=prediction["population_at_risk"],
        confidence=prediction["confidence"],
        timestamp=datetime.utcnow()
    )
