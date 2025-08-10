from typing import Dict, Any
from src.interfaces.speech_factory import ISpeechEngineFactory
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager
from src.engines.openai_speech import OpenAISpeechEngine
from src.engines.groq_speech import GroqSpeechEngine
from src.engines.local_whisper_speech import LocalWhisperEngine


class OpenAISpeechFactory(ISpeechEngineFactory):
    """Factory for creating OpenAI speech engines"""

    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create OpenAI speech engine instance"""
        return OpenAISpeechEngine(settings)

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about OpenAI speech"""
        return {
            "name": "OpenAI Speech",
            "id": "openai",
            "provider": "OpenAI",
            "requires_api_key": True,
            "model": "whisper-1",
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Check if OpenAI speech is available"""
        try:
            api_key = settings.get_provider_api_key("openai")
            return bool(api_key and api_key.strip())
        except Exception:
            return False


class GroqSpeechFactory(ISpeechEngineFactory):
    """Factory for creating Groq speech engines"""

    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create Groq speech engine instance"""
        return GroqSpeechEngine(settings)

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about Groq speech"""
        return {
            "name": "Groq Speech",
            "id": "groq",
            "provider": "Groq",
            "requires_api_key": True,
            "model": "whisper-large-v3",
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Check if Groq speech is available"""
        try:
            api_key = settings.get_provider_api_key("groq")
            return bool(api_key and api_key.strip())
        except Exception:
            return False


class LocalWhisperFactory(ISpeechEngineFactory):
    """Factory for creating Local Whisper engines"""

    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create Local Whisper engine instance"""
        return LocalWhisperEngine(settings)

    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about Local Whisper"""
        return {
            "name": "Local Whisper",
            "id": "local_whisper",
            "provider": "Local",
            "requires_api_key": False,
            "model_sizes": ["tiny", "base", "small", "medium", "large"],
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Local Whisper is available if we can import it (which we already did)"""
        return True
