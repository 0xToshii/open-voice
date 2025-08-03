from abc import ABC, abstractmethod
from typing import Optional


class IAudioRecorder(ABC):
    """Abstract interface for audio recording"""

    @abstractmethod
    def start_recording(self) -> None:
        """Start audio recording"""
        pass

    @abstractmethod
    def stop_recording(self) -> Optional[bytes]:
        """Stop recording and return audio data"""
        pass

    @abstractmethod
    def is_recording(self) -> bool:
        """Check if currently recording"""
        pass

    @abstractmethod
    def get_audio_level(self) -> float:
        """Get current audio level for visualization (0.0 to 1.0)"""
        pass
