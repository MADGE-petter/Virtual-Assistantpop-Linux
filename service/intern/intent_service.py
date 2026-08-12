"""Intent Service - Xử lý intent classification."""
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

from .text_utils import extract_name


class IntentService:
    """Service quản lý intent classification.
    
    Chỉ làm 1 việc: classify intent từ text.
    """
    
    def __init__(self):
        self._classifier = None
        self._init_classifier()
    
    def _init_classifier(self):
        """Lazy init classifier."""
        if self._classifier is None:
            try:
                from service.intern import IntentClassifier
                self._classifier = IntentClassifier
                logger.debug("[IntentService] Classifier initialized")
            except Exception as e:
                logger.error(f"[IntentService] Error loading classifier: {e}")
    
    def classify(self, text: str) -> str:
        """Classify intent từ text."""
        if not self._classifier:
            self._init_classifier()
        
        if self._classifier:
            result = self._classifier.classify(text)
            logger.debug(f"[IntentService] '{text[:30]}...' -> {result}")
            return result
        
        return "unknown"
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract name từ text - delegate to text_utils."""
        return extract_name(text)
