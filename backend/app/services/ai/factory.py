from app.services.ai.satellite import SatelliteClassificationModel
from app.services.ai.weather import WeatherPredictionModel
from app.services.ai.tweet_nlp import TweetNLPModel
from app.services.ai.gemini_rag import GeminiRAGModel

class AIFactory:
    """Thread-safe model factory providing singleton access to AI model stubs."""
    
    # Eager class instantiations ensure thread-safety. Heavy weights loading
    # remains deferred (lazy-loaded) until first execution check.
    _satellite = SatelliteClassificationModel()
    _weather = WeatherPredictionModel()
    _tweet = TweetNLPModel()
    _rag = GeminiRAGModel()

    @classmethod
    def get_satellite_model(cls) -> SatelliteClassificationModel:
        """Retrieves the Satellite Classification Model singleton."""
        return cls._satellite

    @classmethod
    def get_weather_model(cls) -> WeatherPredictionModel:
        """Retrieves the Weather Prediction Model singleton."""
        return cls._weather

    @classmethod
    def get_tweet_model(cls) -> TweetNLPModel:
        """Retrieves the Tweet NLP Model singleton."""
        return cls._tweet

    @classmethod
    def get_gemini_rag_model(cls) -> GeminiRAGModel:
        """Retrieves the Gemini RAG Model singleton."""
        return cls._rag
