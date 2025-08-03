from src.interfaces.data_store import IDataStore, TranscriptEntry
from typing import List
from datetime import datetime, timedelta
import random


class MockDataStore(IDataStore):
    """Mock data store for rapid development and testing"""

    def __init__(self):
        self.transcripts = []
        self.next_id = 1
        self._populate_sample_data()

    def _populate_sample_data(self):
        """Create some sample transcript entries"""
        sample_texts = [
            "Hello there. What is your name?",
            "When I double tap the hotkey, Aqua Voice stays on. When I'm done, I press the key again.",
            "What is your name?",
            "This is a longer transcription to test how the UI handles multiple lines of text and various lengths of content.",
            "Testing the speech to text functionality with this sample.",
            "The quick brown fox jumps over the lazy dog.",
        ]

        for i, text in enumerate(sample_texts):
            timestamp = datetime.now() - timedelta(minutes=random.randint(1, 60))
            duration = random.uniform(1.0, 8.0)
            entry = TranscriptEntry(
                id=self.next_id,
                original_text=text,
                processed_text=text,
                timestamp=timestamp,
                duration=duration,
                inserted_successfully=True,
            )
            self.transcripts.append(entry)
            self.next_id += 1

    def save_transcript(
        self, original_text: str, processed_text: str, duration: float
    ) -> int:
        """Save a transcript entry and return its ID"""
        entry = TranscriptEntry(
            id=self.next_id,
            original_text=original_text,
            processed_text=processed_text,
            timestamp=datetime.now(),
            duration=duration,
            inserted_successfully=False,
        )
        self.transcripts.append(entry)
        self.next_id += 1
        return entry.id

    def get_transcripts(self, limit: int = 100) -> List[TranscriptEntry]:
        """Get recent transcript entries"""
        # Return most recent first
        sorted_transcripts = sorted(
            self.transcripts, key=lambda x: x.timestamp, reverse=True
        )
        return sorted_transcripts[:limit]

    def mark_insertion_status(self, transcript_id: int, success: bool) -> None:
        """Mark whether text insertion was successful"""
        for transcript in self.transcripts:
            if transcript.id == transcript_id:
                transcript.inserted_successfully = success
                break
