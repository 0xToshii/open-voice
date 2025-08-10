from abc import ABC, abstractmethod


class ILLMClient(ABC):
    """Abstract interface for LLM clients (OpenAI, etc.)"""

    @abstractmethod
    def generate(self, system_prompt: str, user_input: str) -> str:
        """
        Generate response using LLM

        Args:
            system_prompt: The system/instruction prompt
            user_input: The user input text to process

        Returns:
            Generated response text

        Raises:
            Exception: If LLM generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if LLM client is available and properly configured

        Returns:
            True if client can be used, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict:
        """
        Get information about the LLM model being used

        Returns:
            Dictionary with model information
        """
        pass
