from abc import ABC, abstractmethod


class ISpeechEngine(ABC):
    """Abstract interface for speech-to-text engines"""

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio data to text"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the engine is available and configured"""
        pass
