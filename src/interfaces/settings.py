from abc import ABC, abstractmethod


class ISettingsManager(ABC):
    """Abstract interface for settings management"""

    @abstractmethod
    def get_cerebras_key(self) -> str:
        """Get Cerebras API key"""
        pass

    @abstractmethod
    def set_cerebras_key(self, key: str) -> None:
        """Set Cerebras API key"""
        pass

    @abstractmethod
    def get_openai_key(self) -> str:
        """Get OpenAI API key"""
        pass

    @abstractmethod
    def set_openai_key(self, key: str) -> None:
        """Set OpenAI API key"""
        pass

    @abstractmethod
    def get_all(self) -> dict:
        """Get all settings as a dictionary"""
        pass
