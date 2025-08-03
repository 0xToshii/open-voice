from src.interfaces.speech import ISpeechEngine
import random
from datetime import datetime


class MockSpeechEngine(ISpeechEngine):
    """Mock speech engine for rapid development and testing"""

    def __init__(self):
        self.mock_responses = [
            "Hello there. What is your name?",
            "When I double tap the hotkey, Aqua Voice stays on. When I'm done, I press the key again.",
            "What is your name?",
            "This is a test transcription from the mock engine.",
            "The quick brown fox jumps over the lazy dog.",
            "Testing speech to text functionality.",
        ]

    def transcribe(self, audio_data: bytes) -> str:
        """Return a random mock transcription"""
        return random.choice(self.mock_responses)

    def is_available(self) -> bool:
        """Mock engine is always available"""
        return True
