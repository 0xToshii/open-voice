from src.interfaces.data_store import IDataStore, TranscriptEntry
from typing import List, Optional
from datetime import datetime, timedelta
import random


class MockDataStore(IDataStore):
    """Mock data store for rapid development and testing"""

    def __init__(self):
        self.transcripts = []
        self.next_id = 1

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
                audio_file_path=None,
                provider_used="mock",
            )
            self.transcripts.append(entry)
            self.next_id += 1

    def save_transcript(
        self,
        original_text: str,
        processed_text: str,
        duration: float,
        audio_file_path: Optional[str] = None,
        provider_used: str = "unknown",
    ) -> int:
        """Save a transcript entry and return its ID"""
        entry = TranscriptEntry(
            id=self.next_id,
            original_text=original_text,
            processed_text=processed_text,
            timestamp=datetime.now(),
            duration=duration,
            inserted_successfully=False,
            audio_file_path=audio_file_path,
            provider_used=provider_used,
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

    def delete_transcript(self, transcript_id: int) -> bool:
        """Delete a transcript entry and its audio file. Returns True if successful"""
        for i, transcript in enumerate(self.transcripts):
            if transcript.id == transcript_id:
                del self.transcripts[i]
                print(f"Deleted transcript {transcript_id}")
                return True
        print(f"Transcript {transcript_id} not found")
        return False

    def get_transcript_audio_path(self, transcript_id: int) -> Optional[str]:
        """Get the audio file path for a transcript"""
        for transcript in self.transcripts:
            if transcript.id == transcript_id:
                return transcript.audio_file_path
        return None

    def save_audio_file(self, audio_data: bytes, transcript_id: int) -> Optional[str]:
        """Save audio data to file and return the file path (mock implementation)"""
        # Mock implementation - just return a fake path for testing
        fake_path = f"/tmp/mock_audio/transcript_{transcript_id}.wav"
        print(f"Mock: Would save {len(audio_data)} bytes to {fake_path}")
        return fake_path

    def update_audio_path(self, transcript_id: int, audio_file_path: str) -> bool:
        """Update the audio file path for a transcript (mock implementation)"""
        for transcript in self.transcripts:
            if transcript.id == transcript_id:
                transcript.audio_file_path = audio_file_path
                print(
                    f"Mock: Updated audio path for transcript {transcript_id} to {audio_file_path}"
                )
                return True
        print(f"Mock: Transcript {transcript_id} not found for audio path update")
        return False
