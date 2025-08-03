from abc import ABC, abstractmethod
from typing import Dict, Any


class ILLMRouter(ABC):
    """Interface for LLM routing and fallback management"""

    @abstractmethod
    def process_with_best_llm(self, system_prompt: str, user_input: str) -> str:
        """
        Process text using the best available LLM with automatic fallback.

        Args:
            system_prompt: The system/instruction prompt for the LLM
            user_input: The user text to process

        Returns:
            Processed text string
        """
        pass

    @abstractmethod
    def get_last_used_llm_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM that was used in the last processing call.

        Returns:
            Dictionary with LLM information (provider, model, success, etc.)
        """
        pass

    @abstractmethod
    def get_available_llms(self) -> list:
        """
        Get list of currently available LLM providers.

        Returns:
            List of available LLM provider names
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the router has at least one available LLM.

        Returns:
            True if at least one LLM is available
        """
        pass
