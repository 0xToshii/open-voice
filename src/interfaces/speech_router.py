from abc import ABC, abstractmethod
from typing import Dict, Any


class ISpeechEngineRouter(ABC):
    """Interface for speech engine routing and fallback management"""

    @abstractmethod
    def transcribe_with_fallback(self, audio_data: bytes) -> str:
        """
        Transcribe audio using the best available engine with automatic fallback.

        Args:
            audio_data: Raw audio bytes to transcribe

        Returns:
            Transcribed text string
        """
        pass

    @abstractmethod
    def get_last_used_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the engine that was used in the last transcription.

        Returns:
            Dictionary with engine information (name, provider, success, etc.)
        """
        pass

    @abstractmethod
    def get_available_engines(self) -> list:
        """
        Get list of currently available speech engines.

        Returns:
            List of available engine names
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the router has at least one available engine.

        Returns:
            True if at least one engine is available
        """
        pass
