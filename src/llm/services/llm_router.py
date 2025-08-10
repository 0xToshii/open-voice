from typing import Dict, Any
from src.llm.interfaces.llm_router import ILLMRouter
from src.llm.interfaces.llm_client import ILLMClient
from src.llm.clients.openai_client import OpenAILLMClient
from src.llm.clients.passthrough_client import PassthroughLLMClient
from src.interfaces.settings import ISettingsManager


class LLMRouter(ILLMRouter):
    """
    Provider-based LLM router that uses the selected provider without fallbacks.
    Maintains dependency inversion by depending only on abstractions.
    """

    def __init__(self, settings_manager: ISettingsManager):
        self.settings_manager = settings_manager

        # Track last used LLM for reporting
        self._last_llm_info = {
            "provider": "None",
            "model": "None",
            "success": False,
            "error": None,
        }

    def process_with_best_llm(self, system_prompt: str, user_input: str) -> str:
        """Process text using selected provider only (no fallbacks)"""
        if not user_input or not user_input.strip():
            self._last_llm_info = {
                "provider": "None",
                "model": "None",
                "success": False,
                "error": "No input text provided",
            }
            return user_input

        # Get selected provider
        selected_provider = self.settings_manager.get_selected_provider()

        try:
            # Create LLM client for selected provider
            llm_client = self._create_llm_for_provider(selected_provider)

            if not llm_client:
                raise Exception(
                    f"No LLM client available for provider: {selected_provider}"
                )

            # Check if client is available
            if not llm_client.is_available():
                if selected_provider == "local":
                    # Local provider should always be available (passthrough)
                    pass
                else:
                    raise Exception(
                        f"{selected_provider} provider not available - check API key"
                    )

            print(f"Using {selected_provider} LLM provider")

            # Process with selected provider
            result = llm_client.generate(system_prompt, user_input)

            # Record successful LLM use
            model_info = llm_client.get_model_info()
            self._last_llm_info = {
                "provider": model_info.get("provider", selected_provider),
                "model": model_info.get("model", "unknown"),
                "success": True,
                "error": None,
            }

            return result.strip() if result else user_input

        except Exception as e:
            print(f"LLM processing failed with {selected_provider} provider: {e}")

            # Record failure
            self._last_llm_info = {
                "provider": selected_provider,
                "model": "unknown",
                "success": False,
                "error": str(e),
            }

            # No fallback - raise exception to inform user
            raise Exception(f"LLM processing failed: {e}")

    def _create_llm_for_provider(self, provider: str) -> ILLMClient:
        """Create LLM client for the specified provider"""
        if provider == "openai":
            return OpenAILLMClient(self.settings_manager)
        elif provider == "local":
            return PassthroughLLMClient()
        else:
            raise Exception(f"Unknown provider: {provider}")

    def get_last_used_llm_info(self) -> Dict[str, Any]:
        """Get information about the LLM used in the last processing call"""
        return self._last_llm_info.copy()

    def get_available_llms(self) -> list:
        """Get list of currently available LLM providers for selected provider"""
        try:
            selected_provider = self.settings_manager.get_selected_provider()
            provider_name = selected_provider.capitalize()

            # Check if the LLM client for this provider is actually available
            llm_client = self._create_llm_for_provider(selected_provider)

            if llm_client.is_available():
                return [provider_name]
            else:
                return []
        except Exception:
            return []

    def is_available(self) -> bool:
        """Check if selected provider is available"""
        try:
            selected_provider = self.settings_manager.get_selected_provider()
            llm_client = self._create_llm_for_provider(selected_provider)
            return llm_client.is_available()
        except Exception:
            return False
