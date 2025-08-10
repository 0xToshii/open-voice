from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TranscriptEntry:
    id: int
    original_text: str
    processed_text: Optional[str]
    timestamp: datetime
    duration: float
    inserted_successfully: bool
    audio_file_path: Optional[str]
    provider_used: str


class IDataStore(ABC):
    """Abstract interface for data persistence"""

    @abstractmethod
    def save_transcript(
        self,
        original_text: str,
        processed_text: str,
        duration: float,
        audio_file_path: Optional[str] = None,
        provider_used: str = "unknown",
    ) -> int:
        """Save a transcript entry and return its ID"""
        pass

    @abstractmethod
    def get_transcripts(self, limit: int = 100) -> List[TranscriptEntry]:
        """Get recent transcript entries"""
        pass

    @abstractmethod
    def mark_insertion_status(self, transcript_id: int, success: bool) -> None:
        """Mark whether text insertion was successful"""
        pass

    @abstractmethod
    def delete_transcript(self, transcript_id: int) -> bool:
        """Delete a transcript entry and its audio file. Returns True if successful"""
        pass

    @abstractmethod
    def get_transcript_audio_path(self, transcript_id: int) -> Optional[str]:
        """Get the audio file path for a transcript"""
        pass

    @abstractmethod
    def save_audio_file(self, audio_data: bytes, transcript_id: int) -> Optional[str]:
        """Save audio data to file and return the file path"""
        pass

    @abstractmethod
    def update_audio_path(self, transcript_id: int, audio_file_path: str) -> bool:
        """Update the audio file path for a transcript"""
        pass
