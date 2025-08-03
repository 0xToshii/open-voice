from typing import Dict, Any, List, Tuple, Callable
from src.interfaces.speech_router import ISpeechEngineRouter
from src.interfaces.speech_factory import ISpeechEngineRegistry
from src.interfaces.settings import ISettingsManager


class SpeechEngineRouter(ISpeechEngineRouter):
    """
    Speech engine router that handles dynamic engine selection and fallback logic.
    Maintains dependency inversion by depending only on abstractions.
    """

    def __init__(
        self, speech_registry: ISpeechEngineRegistry, settings_manager: ISettingsManager
    ):
        self.speech_registry = speech_registry
        self.settings_manager = settings_manager

        # Track last used engine for reporting
        self._last_engine_info = {
            "name": "None",
            "provider": "None",
            "success": False,
            "error": None,
        }

    def transcribe_with_fallback(self, audio_data: bytes) -> str:
        """Transcribe audio using priority-based engine selection with fallback"""
        if not audio_data:
            self._last_engine_info = {
                "name": "None",
                "provider": "None",
                "success": False,
                "error": "No audio data provided",
            }
            return "No audio data received"

        # Get engines to try in priority order
        engines_to_try = self._get_engines_in_priority_order()

        if not engines_to_try:
            self._last_engine_info = {
                "name": "None",
                "provider": "None",
                "success": False,
                "error": "No speech engines available",
            }
            return "No speech engines available"

        # Attempt each engine in order
        for engine_name, engine_creator in engines_to_try:
            try:
                print(f"🎤 Attempting: {engine_name}")

                # Create engine on demand (fresh instance each time)
                engine = engine_creator()

                # Attempt transcription
                result = engine.transcribe(audio_data)

                # Check if result is valid
                if result and result.strip() and not self._is_error_result(result):
                    print(f"✅ Success with: {engine_name}")

                    # Record successful engine use
                    self._last_engine_info = {
                        "name": engine_name,
                        "provider": self._get_engine_provider(engine_name),
                        "success": True,
                        "error": None,
                    }

                    return result.strip()
                else:
                    print(f"⚠️ {engine_name} returned empty/invalid result: '{result}'")

            except Exception as e:
                print(f"❌ {engine_name} failed: {e}")
                continue

        # All engines failed
        print("❌ All speech engines failed")
        self._last_engine_info = {
            "name": "All engines",
            "provider": "Multiple",
            "success": False,
            "error": "All speech engines failed",
        }
        return "Speech recognition failed - all engines unavailable"

    def _get_engines_in_priority_order(self) -> List[Tuple[str, Callable]]:
        """Get list of engines to try in priority order based on current settings"""
        engines_to_try = []

        # 1. Try OpenAI Whisper first if API key is available
        openai_key = self.settings_manager.get_openai_key()
        if openai_key and openai_key.strip():
            engines_to_try.append(
                (
                    "OpenAI Whisper",
                    lambda: self.speech_registry.create_engine_by_name(
                        "openai", self.settings_manager
                    ),
                )
            )

        # 2. Try Google Speech Recognition as fallback
        engines_to_try.append(
            (
                "Google Speech",
                lambda: self.speech_registry.create_engine_by_name(
                    "google", self.settings_manager
                ),
            )
        )

        # 3. Try Mock engine as final fallback
        engines_to_try.append(
            (
                "Mock Speech",
                lambda: self.speech_registry.create_engine_by_name(
                    "mock", self.settings_manager
                ),
            )
        )

        return engines_to_try

    def _is_error_result(self, result: str) -> bool:
        """Check if the result indicates an error condition"""
        if not result:
            return True

        error_indicators = [
            "error:",
            "failed",
            "recognition error",
            "service error",
            "could not understand",
            "speech not clear",
        ]

        result_lower = result.lower()
        return any(indicator in result_lower for indicator in error_indicators)

    def _get_engine_provider(self, engine_name: str) -> str:
        """Get the provider name for an engine"""
        provider_map = {
            "OpenAI Whisper": "OpenAI",
            "Google Speech": "Google",
            "Mock Speech": "Mock",
        }
        return provider_map.get(engine_name, "Unknown")

    def get_last_used_engine_info(self) -> Dict[str, Any]:
        """Get information about the engine used in the last transcription"""
        return self._last_engine_info.copy()

    def get_available_engines(self) -> List[str]:
        """Get list of currently available speech engines"""
        try:
            available_engines = self.speech_registry.get_available_engines(
                self.settings_manager
            )
            return [engine.get("name", "Unknown") for engine in available_engines]
        except Exception as e:
            print(f"❌ Error getting available engines: {e}")
            return []

    def is_available(self) -> bool:
        """Check if at least one speech engine is available"""
        try:
            available_engines = self.get_available_engines()
            return len(available_engines) > 0
        except Exception:
            return False


class MockSpeechEngineRouter(ISpeechEngineRouter):
    """Mock speech engine router for testing"""

    def __init__(self):
        self._last_engine_info = {
            "name": "MockEngine",
            "provider": "Mock",
            "success": True,
            "error": None,
        }

    def transcribe_with_fallback(self, audio_data: bytes) -> str:
        """Mock transcription with simulated processing"""
        if not audio_data:
            return "No audio data received"

        print("🎤 Mock Router: Processing audio with fallback")
        print("✅ Mock Router: Success with MockEngine")

        # Return mock transcription
        return "This is a mock transcription from the router."

    def get_last_used_engine_info(self) -> Dict[str, Any]:
        """Get mock engine info"""
        return self._last_engine_info.copy()

    def get_available_engines(self) -> List[str]:
        """Get mock available engines"""
        return ["MockEngine"]

    def is_available(self) -> bool:
        """Mock router is always available"""
        return True
