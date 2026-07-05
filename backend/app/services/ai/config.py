from pydantic import BaseModel

class AIConfig(BaseModel):
    """Configuration settings specifically for model paths, templates, and execution parameters."""
    
    # Model Weights Storage
    SATELLITE_MODEL_PATH: str = "ml/models/satellite.onnx"
    WEATHER_MODEL_PATH: str = "ml/models/weather.onnx"
    TWEET_MODEL_PATH: str = "ml/models/tweet_nlp.onnx"
    
    # Prompt Management Definitions
    RAG_REPORT_PROMPT_TEMPLATE: str = (
        "Context: Correlate local meteorological sensors, social media logs, and spatial feeds.\n"
        "Coordinates: Latitude {latitude}, Longitude {longitude}.\n"
        "Identified Incidents:\n{incidents}\n"
        "Task: Compile a structured disaster situation report summary with key risk indicators."
    )
    
    # Error Recovery & Retry settings
    INFERENCE_MAX_RETRIES: int = 3
    INFERENCE_RETRY_BACKOFF: float = 1.5
    
    # AI Architecture Targets (Making local execution compatible with Ray or Triton stubs)
    SERVING_MODE: str = "LOCAL"  # Options: LOCAL, RAY, TRITON
    RAY_SERVE_URL: str = "http://localhost:8000/predict"
    TRITON_SERVER_URL: str = "http://localhost:8001/v2/models"

ai_settings = AIConfig()
