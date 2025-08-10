from typing import Dict, Any, List, Tuple, Callable
from src.llm.interfaces.llm_router import ILLMRouter
from src.llm.interfaces.llm_client import ILLMClient
from src.llm.clients.cerebras_client import CerebrasLLMClient
from src.llm.clients.passthrough_client import PassthroughLLMClient
from src.interfaces.settings import ISettingsManager


class LLMRouter(ILLMRouter):
    """
    LLM router that handles dynamic client selection and fallback logic.
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
        """Process text using priority-based LLM selection with fallback"""
        if not user_input or not user_input.strip():
            self._last_llm_info = {
                "provider": "None",
                "model": "None",
                "success": False,
                "error": "No input text provided",
            }
            return user_input

        # Get LLMs to try in priority order
        llms_to_try = self._get_llms_in_priority_order()

        if not llms_to_try:
            self._last_llm_info = {
                "provider": "None",
                "model": "None",
                "success": False,
                "error": "No LLM clients available",
            }
            return user_input

        # Attempt each LLM in order
        for llm_name, llm_creator in llms_to_try:
            try:
                print(f"Attempting: {llm_name}")

                # Create LLM client on demand (fresh instance each time)
                llm_client = llm_creator()

                # Check if client is available (has valid key)
                if not llm_client.is_available():
                    print(f"{llm_name} not available (no valid key)")
                    continue

                # Attempt processing
                result = llm_client.generate(system_prompt, user_input)

                # Check if result is valid
                if result and result.strip():
                    print(f"Success with: {llm_name}")

                    # Record successful LLM use
                    model_info = llm_client.get_model_info()
                    self._last_llm_info = {
                        "provider": model_info.get("provider", llm_name),
                        "model": model_info.get("model", "unknown"),
                        "success": True,
                        "error": None,
                    }

                    return result.strip()
                else:
                    print(f"{llm_name} returned empty result")

            except Exception as e:
                print(f"{llm_name} failed: {e}")
                continue

        # All LLMs failed
        print("All LLM clients failed")
        self._last_llm_info = {
            "provider": "All providers",
            "model": "Multiple",
            "success": False,
            "error": "All LLM clients failed",
        }
        return user_input  # Return original text as fallback

    def _get_llms_in_priority_order(self) -> List[Tuple[str, Callable]]:
        """Get list of LLMs to try in priority order based on current settings"""
        llms_to_try = []

        # 1. Try Cerebras first if API key is available
        cerebras_key = self.settings_manager.get_cerebras_key()
        if cerebras_key and cerebras_key.strip():
            llms_to_try.append(
                ("Cerebras", lambda: CerebrasLLMClient(self.settings_manager))
            )

        # 2. Always add Passthrough as final fallback
        llms_to_try.append(("Passthrough LLM", lambda: PassthroughLLMClient()))

        return llms_to_try

    def get_last_used_llm_info(self) -> Dict[str, Any]:
        """Get information about the LLM used in the last processing call"""
        return self._last_llm_info.copy()

    def get_available_llms(self) -> List[str]:
        """Get list of currently available LLM providers"""
        available_llms = []

        try:
            # Check Cerebras availability
            cerebras_key = self.settings_manager.get_cerebras_key()
            if cerebras_key and cerebras_key.strip():
                # Create client to test if it's truly available
                try:
                    cerebras_client = CerebrasLLMClient(self.settings_manager)
                    if cerebras_client.is_available():
                        available_llms.append("Cerebras")
                except Exception:
                    pass  # Cerebras not available

            # Passthrough is always available
            available_llms.append("Passthrough LLM")

        except Exception as e:
            print(f"Error checking available LLMs: {e}")
            # Fallback to Passthrough only
            available_llms = ["Passthrough LLM"]

        return available_llms

    def is_available(self) -> bool:
        """Check if at least one LLM is available"""
        try:
            available_llms = self.get_available_llms()
            return len(available_llms) > 0
        except Exception:
            return True  # Passthrough is always available as fallback
