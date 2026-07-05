import logging
import os
import time
from typing import Any, Callable
from app.services.ai.config import ai_settings

logger = logging.getLogger(__name__)

# Verify onnxruntime is installed before attempting to resolve session providers
try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False

class ONNXInferenceSession:
    """Session wrapper for ONNX Runtime engines, fallback-capable for zero-crash assurances."""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.session = None

    def load(self) -> bool:
        """Attempts to mount the ONNX session; registers warnings on missing runtimes/files."""
        if not HAS_ORT:
            logger.warning(
                f"onnxruntime is not installed. Falling back to baseline simulation "
                f"for model: {self.model_path}"
            )
            return False
            
        if not os.path.exists(self.model_path):
            logger.warning(
                f"ONNX model file not found at {self.model_path}. "
                f"Utilizing simulation baselines."
            )
            return False

        try:
            self.session = ort.InferenceSession(
                self.model_path,
                providers=["CPUExecutionProvider"]
            )
            logger.info(f"Successfully loaded ONNX runtime session: {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed loading ONNX model weights ({self.model_path}): {str(e)}")
            return False

    def run(self, input_feed: dict) -> Any:
        """Executes forward-pass inference on the ONNX session if active."""
        if self.session:
            return self.session.run(None, input_feed)
        return None

def execute_with_retry(func: Callable, *args, **kwargs) -> Any:
    """Executes a callable inference routine with exponential backoff on exceptions."""
    max_retries = ai_settings.INFERENCE_MAX_RETRIES
    backoff = ai_settings.INFERENCE_RETRY_BACKOFF
    retries = 0
    
    while retries < max_retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Inference execution failed after {max_retries} attempts: {str(e)}")
                raise
            sleep_time = backoff ** retries
            logger.warning(
                f"Inference attempt {retries}/{max_retries} failed. "
                f"Retrying in {sleep_time:.2f}s... Error: {str(e)}"
            )
            time.sleep(sleep_time)
