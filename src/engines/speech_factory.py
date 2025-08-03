from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager
from src.engines.openai_speech import OpenAIWhisperEngine
from src.engines.speech_engine import SpeechRecognitionEngine
from src.engines.mock_speech import MockSpeechEngine


class SpeechEngineFactory:
    """Factory for creating the best available speech recognition engine"""

    @staticmethod
    def create_best_engine(
        settings_manager: ISettingsManager, use_mock: bool = False
    ) -> ISpeechEngine:
        """Create the best available speech engine based on configuration"""

        if use_mock:
            print("🎭 Using mock speech engine for testing")
            return MockSpeechEngine()

        # Try OpenAI Whisper first (best accuracy)
        try:
            openai_engine = OpenAIWhisperEngine(settings_manager)
            if openai_engine.is_available():
                print("🚀 Using OpenAI Whisper engine")
                return openai_engine
            else:
                print("⚠️ OpenAI Whisper not available (no API key)")
        except Exception as e:
            print(f"⚠️ OpenAI Whisper initialization failed: {e}")

        # Fallback to Google Speech Recognition
        try:
            google_engine = SpeechRecognitionEngine("google")
            if google_engine.is_available():
                print("🌐 Using Google Speech Recognition engine")
                return google_engine
            else:
                print("⚠️ Google Speech Recognition not available")
        except Exception as e:
            print(f"⚠️ Google Speech Recognition failed: {e}")

        # Final fallback to mock engine
        print("🎭 Falling back to mock speech engine")
        return MockSpeechEngine()

    @staticmethod
    def create_openai_engine(settings_manager: ISettingsManager) -> OpenAIWhisperEngine:
        """Create OpenAI Whisper engine specifically"""
        return OpenAIWhisperEngine(settings_manager)

    @staticmethod
    def create_google_engine() -> SpeechRecognitionEngine:
        """Create Google Speech Recognition engine specifically"""
        return SpeechRecognitionEngine("google")

    @staticmethod
    def create_mock_engine() -> MockSpeechEngine:
        """Create mock speech engine for testing"""
        return MockSpeechEngine()

    @staticmethod
    def get_available_engines(settings_manager: ISettingsManager) -> list[dict]:
        """Get list of available speech engines with their info"""
        engines = []

        # Check OpenAI Whisper
        try:
            openai_engine = OpenAIWhisperEngine(settings_manager)
            engines.append(
                {
                    "name": "OpenAI Whisper",
                    "id": "openai",
                    "available": openai_engine.is_available(),
                    "info": openai_engine.get_model_info(),
                }
            )
        except:
            engines.append(
                {
                    "name": "OpenAI Whisper",
                    "id": "openai",
                    "available": False,
                    "info": {"error": "Failed to initialize"},
                }
            )

        # Check Google Speech Recognition
        try:
            google_engine = SpeechRecognitionEngine("google")
            engines.append(
                {
                    "name": "Google Speech Recognition",
                    "id": "google",
                    "available": google_engine.is_available(),
                    "info": {
                        "name": "Google Speech Recognition",
                        "provider": "Google",
                        "accuracy": "Good",
                        "language_support": "Multilingual",
                        "requires_internet": True,
                        "requires_api_key": False,
                    },
                }
            )
        except:
            engines.append(
                {
                    "name": "Google Speech Recognition",
                    "id": "google",
                    "available": False,
                    "info": {"error": "Failed to initialize"},
                }
            )

        # Mock is always available
        engines.append(
            {
                "name": "Mock Engine (Testing)",
                "id": "mock",
                "available": True,
                "info": {
                    "name": "Mock Speech Engine",
                    "provider": "Internal",
                    "accuracy": "Perfect (Mock)",
                    "language_support": "English",
                    "requires_internet": False,
                    "requires_api_key": False,
                },
            }
        )

        return engines
