from abc import ABC, abstractmethod
from typing import Any

class BaseAIModel(ABC):
    """Abstract base class establishing the shared interface for all AI models."""

    def __init__(self):
        self.is_loaded = False

    @abstractmethod
    def load_model(self) -> None:
        """Loads model weights, assets, or ONNX runtime sessions. Supports lazy loading."""
        pass

    @abstractmethod
    def predict(self, input_data: Any) -> Any:
        """Executes forward-pass prediction inference on input parameters."""
        pass

    def ensure_loaded(self) -> None:
        """Helper checking load state before executing predict blocks, lazy loading on-demand."""
        if not self.is_loaded:
            self.load_model()
