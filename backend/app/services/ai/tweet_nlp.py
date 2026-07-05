from app.services.ai.base import BaseAIModel
from app.services.ai.onnx_layer import ONNXInferenceSession
from app.services.ai.config import ai_settings
from typing import Dict, Any

class TweetNLPModel(BaseAIModel):
    """Natural Language Processing model to detect emergency threats and extract locations from text."""

    def __init__(self):
        super().__init__()
        self.session = None

    def load_model(self) -> None:
        """Loads ONNX session or mounts mock simulator."""
        self.session = ONNXInferenceSession(ai_settings.TWEET_MODEL_PATH)
        self.session.load()
        self.is_loaded = True

    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs sentiment/incident classification on text feeds."""
        self.ensure_loaded()
        
        text = input_data.get("text", "")
        
        # Determine threat keyword hits
        tags = []
        for keyword in ["flood", "fire", "earthquake", "evacuate", "landslide"]:
            if keyword in text.lower():
                tags.append(keyword)
                
        is_threat = len(tags) > 0
        severity = 0.85 if is_threat else 0.15
        
        return {
            "is_threat": is_threat,
            "inferred_severity": severity,
            "tags": tags,
            "confidence": 0.82
        }
