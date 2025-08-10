from typing import Dict, Any
from src.interfaces.speech_router import ISpeechEngineRouter
from src.interfaces.speech_factory import ISpeechEngineRegistry
from src.interfaces.settings import ISettingsManager
from src.interfaces.speech import ISpeechEngine


class SpeechEngineRouter(ISpeechEngineRouter):
    """
    Provider-based speech engine router that uses the selected provider without fallbacks.
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
        """Transcribe audio using selected provider only (no fallbacks)"""
        if not audio_data:
            self._last_engine_info = {
                "name": "None",
                "provider": "None",
                "success": False,
                "error": "No audio data provided",
            }
            return "No audio data received"

        # Get selected provider
        selected_provider = self.settings_manager.get_selected_provider()

        try:
            # Get engine ID for selected provider
            engine_id = self._get_engine_id_for_provider(selected_provider)

            if not engine_id:
                raise Exception(
                    f"No speech engine available for provider: {selected_provider}"
                )

            print(f"Using {selected_provider} speech provider")

            # Create engine for selected provider
            engine = self.speech_registry.create_engine_by_name(
                engine_id, self.settings_manager
            )

            # Check if engine is available
            if not engine.is_available():
                if selected_provider == "local":
                    # Local provider should always be available
                    pass
                else:
                    raise Exception(
                        f"{selected_provider} speech engine not available - check API key"
                    )

            # Transcribe with selected provider
            result = engine.transcribe(audio_data)

            # Record successful engine use
            self._last_engine_info = {
                "name": self._get_engine_name_for_provider(selected_provider),
                "provider": selected_provider,
                "success": True,
                "error": None,
            }

            return result.strip() if result else "Could not understand audio"

        except Exception as e:
            print(f"Speech transcription failed with {selected_provider} provider: {e}")

            # Record failure
            self._last_engine_info = {
                "name": self._get_engine_name_for_provider(selected_provider),
                "provider": selected_provider,
                "success": False,
                "error": str(e),
            }

            # No fallback - raise exception to inform user
            raise Exception(f"Speech transcription failed: {e}")

    def _get_engine_id_for_provider(self, provider: str) -> str:
        """Get engine ID for the specified provider"""
        provider_engine_map = {
            "openai": "openai",
            "local": "local_whisper",
        }

        engine_id = provider_engine_map.get(provider)
        if not engine_id:
            raise Exception(f"Unknown provider: {provider}")

        return engine_id

    def _get_engine_name_for_provider(self, provider: str) -> str:
        """Get human-readable engine name for the specified provider"""
        provider_name_map = {
            "openai": "OpenAI Whisper",
            "local": "Local Whisper",
        }
        return provider_name_map.get(provider, "Unknown")

    def get_last_used_engine_info(self) -> Dict[str, Any]:
        """Get information about the engine used in the last transcription"""
        return self._last_engine_info.copy()

    def get_available_engines(self) -> list:
        """Get list of currently available speech engines for selected provider"""
        try:
            selected_provider = self.settings_manager.get_selected_provider()
            engine_name = self._get_engine_name_for_provider(selected_provider)

            # Check if the engine for this provider is actually available
            engine_id = self._get_engine_id_for_provider(selected_provider)
            engine = self.speech_registry.create_engine_by_name(
                engine_id, self.settings_manager
            )

            if engine.is_available():
                return [engine_name]
            else:
                return []
        except Exception:
            return []

    def is_available(self) -> bool:
        """Check if selected provider is available"""
        try:
            selected_provider = self.settings_manager.get_selected_provider()
            engine_id = self._get_engine_id_for_provider(selected_provider)
            engine = self.speech_registry.create_engine_by_name(
                engine_id, self.settings_manager
            )
            return engine.is_available()
        except Exception:
            return False
