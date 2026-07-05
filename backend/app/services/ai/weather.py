from app.services.ai.base import BaseAIModel
from app.services.ai.onnx_layer import ONNXInferenceSession
from app.services.ai.config import ai_settings
from typing import Dict, Any

class WeatherPredictionModel(BaseAIModel):
    """Predicts extreme meteorological conditions using rainfall and wind telemetry."""

    def __init__(self):
        super().__init__()
        self.session = None

    def load_model(self) -> None:
        """Loads ONNX session or mounts mock simulator."""
        self.session = ONNXInferenceSession(ai_settings.WEATHER_MODEL_PATH)
        self.session.load()
        self.is_loaded = True

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies weather threat markers."""
        self.ensure_loaded()
        
        rainfall = input_data.get("rainfall", 0.0)
        wind_speed = input_data.get("wind_speed", 0.0)
        
        prediction = "normal"
        if rainfall > 120.0:
            prediction = "severe_deluge"
        elif wind_speed > 45.0:
            prediction = "storm_surge"
            
        return {
            "prediction": prediction,
            "rainfall_expected": rainfall,
            "wind_expected": wind_speed,
            "confidence": 0.88
        }
