from typing import Dict, Any, List, Tuple
from src.interfaces.speech_router import ISpeechEngineRouter
from src.interfaces.speech_factory import ISpeechEngineRegistry
from src.interfaces.settings import ISettingsManager
from src.interfaces.speech import ISpeechEngine


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

        # Engine caching for performance
        self._engine_cache: Dict[str, ISpeechEngine] = {}

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
        for engine_name, engine_id in engines_to_try:
            try:
                print(f"Attempting: {engine_name}")

                # Use cached engine or create if not exists
                engine = self._get_cached_engine(engine_id)

                # Attempt transcription
                result = engine.transcribe(audio_data)

                # Check if result is valid
                if result and result.strip() and not self._is_error_result(result):
                    print(f"Success with: {engine_name}")

                    # Record successful engine use
                    self._last_engine_info = {
                        "name": engine_name,
                        "provider": self._get_engine_provider(engine_name),
                        "success": True,
                        "error": None,
                    }

                    return result.strip()
                else:
                    print(f"{engine_name} returned empty/invalid result: '{result}'")

            except Exception as e:
                print(f"{engine_name} failed: {e}")
                continue

        # All engines failed
        print("All speech engines failed")
        self._last_engine_info = {
            "name": "All engines",
            "provider": "Multiple",
            "success": False,
            "error": "All speech engines failed",
        }
        return "Speech recognition failed - all engines unavailable"

    def _get_engines_in_priority_order(self) -> List[Tuple[str, str]]:
        """Get list of engines to try in priority order from registry"""
        engines_to_try = []

        try:
            # Get available engines from registry (already in priority order)
            available_engines = self.speech_registry.get_available_engines(
                self.settings_manager
            )

            for engine_info in available_engines:
                if engine_info.get("available", False):
                    engine_name = engine_info.get("name", "Unknown")
                    engine_id = engine_info.get("id", "unknown")

                    engines_to_try.append((engine_name, engine_id))
        except Exception as e:
            print(f"Error getting engines from registry: {e}")

        return engines_to_try

    def _get_cached_engine(self, engine_id: str) -> ISpeechEngine:
        """Get cached engine instance or create new one if not cached"""
        if engine_id not in self._engine_cache:
            print(f"Creating and caching engine: {engine_id}")
            engine = self.speech_registry.create_engine_by_name(
                engine_id, self.settings_manager
            )
            self._engine_cache[engine_id] = engine
        else:
            print(f"Using cached engine: {engine_id}")

        return self._engine_cache[engine_id]

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
            "Google Speech Recognition": "Google",
            "Local Whisper": "Local",
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
            print(f"Error getting available engines: {e}")
            return []

    def is_available(self) -> bool:
        """Check if at least one speech engine is available"""
        try:
            available_engines = self.get_available_engines()
            return len(available_engines) > 0
        except Exception:
            return False
