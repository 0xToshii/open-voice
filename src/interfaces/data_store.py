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


class IDataStore(ABC):
    """Abstract interface for data persistence"""

    @abstractmethod
    def save_transcript(
        self, original_text: str, processed_text: str, duration: float
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
