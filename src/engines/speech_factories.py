from typing import Dict, Any
from src.interfaces.speech_factory import ISpeechEngineFactory
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager
from src.engines.openai_speech import OpenAIWhisperEngine
from src.engines.speech_engine import SpeechRecognitionEngine
from src.engines.mock_speech import MockSpeechEngine


class OpenAIWhisperFactory(ISpeechEngineFactory):
    """Factory for creating OpenAI Whisper engines"""

    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create OpenAI Whisper engine instance"""
        return OpenAIWhisperEngine(settings)

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about OpenAI Whisper"""
        return {
            "name": "OpenAI Whisper",
            "id": "openai",
            "provider": "OpenAI",
            "accuracy": "High",
            "language_support": "Multilingual",
            "requires_internet": True,
            "requires_api_key": True,
            "model": "whisper-1",
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Check if OpenAI Whisper is available"""
        try:
            api_key = settings.get_openai_key()
            return bool(api_key and api_key.strip())
        except Exception:
            return False


class GoogleSpeechFactory(ISpeechEngineFactory):
    """Factory for creating Google Speech Recognition engines"""

    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create Google Speech Recognition engine instance"""
        return SpeechRecognitionEngine("google")

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about Google Speech Recognition"""
        return {
            "name": "Google Speech Recognition",
            "id": "google",
            "provider": "Google",
            "accuracy": "Good",
            "language_support": "Multilingual",
            "requires_internet": True,
            "requires_api_key": False,
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Check if Google Speech Recognition is available"""
        try:
            # Google Speech Recognition is generally available if SpeechRecognition package is installed
            engine = SpeechRecognitionEngine("google")
            return engine.is_available()
        except Exception:
            return False


class MockSpeechFactory(ISpeechEngineFactory):
    """Factory for creating Mock speech engines"""

    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create Mock speech engine instance"""
        return MockSpeechEngine()

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about Mock speech engine"""
        return {
            "name": "Mock Speech Engine",
            "id": "mock",
            "provider": "Internal",
            "accuracy": "Perfect (Mock)",
            "language_support": "English",
            "requires_internet": False,
            "requires_api_key": False,
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Mock engine is always available"""
        return True
