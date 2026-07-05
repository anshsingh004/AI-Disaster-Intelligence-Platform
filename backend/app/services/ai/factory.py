from app.services.ai.satellite import SatelliteClassificationModel
from app.services.ai.weather import WeatherPredictionModel
from app.services.ai.tweet_nlp import TweetNLPModel
from app.services.ai.gemini_rag import GeminiRAGModel

class AIFactory:
    """Model factory providing singleton access to AI model stubs."""
    
    _instances = {}

    @classmethod
    def get_satellite_model(cls) -> SatelliteClassificationModel:
        """Retrieves or instantiates the Satellite Classification Model singleton."""
        if "satellite" not in cls._instances:
            cls._instances["satellite"] = SatelliteClassificationModel()
        return cls._instances["satellite"]

    @classmethod
    def get_weather_model(cls) -> WeatherPredictionModel:
        """Retrieves or instantiates the Weather Prediction Model singleton."""
        if "weather" not in cls._instances:
            cls._instances["weather"] = WeatherPredictionModel()
        return cls._instances["weather"]

    @classmethod
    def get_tweet_model(cls) -> TweetNLPModel:
        """Retrieves or instantiates the Tweet NLP Model singleton."""
        if "tweet" not in cls._instances:
            cls._instances["tweet"] = TweetNLPModel()
        return cls._instances["tweet"]

    @classmethod
    def get_gemini_rag_model(cls) -> GeminiRAGModel:
        """Retrieves or instantiates the Gemini RAG Model singleton."""
        if "rag" not in cls._instances:
            cls._instances["rag"] = GeminiRAGModel()
        return cls._instances["rag"]
