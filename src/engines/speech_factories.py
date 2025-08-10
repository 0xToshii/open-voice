from typing import Dict, Any
from src.interfaces.speech_factory import ISpeechEngineFactory
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager
from src.engines.openai_speech import OpenAIWhisperEngine
from src.engines.local_whisper_speech import LocalWhisperEngine


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
            "requires_internet": False,
            "requires_api_key": False,
            "model_sizes": ["tiny", "base", "small", "medium", "large"],
        }

    def is_available(self, settings: ISettingsManager) -> bool:
        """Local Whisper is available if we can import it (which we already did)"""
        return True
