from abc import ABC, abstractmethod
from typing import Optional


class ISettingsManager(ABC):
    """Abstract interface for settings management"""

    @abstractmethod
    def get_selected_provider(self) -> str:
        """Get selected provider name (e.g., 'openai', 'local')"""
        pass

    @abstractmethod
    def set_selected_provider(self, provider: str) -> None:
        """Set selected provider name"""
        pass

    @abstractmethod
    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specified provider"""
        pass

    @abstractmethod
    def set_provider_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for specified provider"""
        pass

    @abstractmethod
    def get_custom_instructions(self) -> str:
        """Get custom instructions"""
        pass

    @abstractmethod
    def set_custom_instructions(self, instructions: str) -> None:
        """Set custom instructions"""
        pass

    @abstractmethod
    def get_all(self) -> dict:
        """Get all settings as a dictionary"""
        pass
