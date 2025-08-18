from PySide6.QtCore import QObject, Signal
from typing import Optional
from abc import ABCMeta
from src.interfaces.settings import ISettingsManager


class ABCQObjectMeta(type(QObject), ABCMeta):
    """Custom metaclass that combines QObject and ABC metaclasses"""

    pass


class SettingsManager(QObject, ISettingsManager, metaclass=ABCQObjectMeta):
    """Simple in-memory settings manager implementing ISettingsManager with provider-based architecture"""

    # Signal emitted when settings change
    setting_changed = Signal(str, str)  # (setting_name, new_value)

    def __init__(self):
        super().__init__()

        # Settings storage (in-memory, no persistence)
        self._settings = {
            "selected_provider": "local",  # Default to local provider
            "provider_api_keys": {
                "openai": "",
                "groq": "",
            },
            "custom_instructions": "",
            "selected_microphone_id": "default",  # Default to system default
            "selected_microphone_name": "Default",  # Display name for UI
        }

    def get_selected_provider(self) -> str:
        """Get selected provider name (e.g., 'openai', 'local')"""
        return self._settings["selected_provider"]

    def set_selected_provider(self, provider: str) -> None:
        """Set selected provider name"""
        valid_providers = ["openai", "groq", "local"]
        if provider not in valid_providers:
            raise ValueError(
                f"Invalid provider '{provider}'. Must be one of: {valid_providers}"
            )

        self._settings["selected_provider"] = provider
        self.setting_changed.emit("selected_provider", provider)
        print(f"Provider updated to: {provider}")

    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specified provider"""
        if provider == "local":
            return None  # Local provider doesn't need API key

        return self._settings["provider_api_keys"].get(provider, "")

    def set_provider_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for specified provider"""
        if provider == "local":
            print("Local provider doesn't require an API key")
            return

        if provider not in self._settings["provider_api_keys"]:
            self._settings["provider_api_keys"][provider] = ""

        self._settings["provider_api_keys"][provider] = api_key
        self.setting_changed.emit(f"provider_api_key_{provider}", api_key)

    def get_custom_instructions(self) -> str:
        """Get custom instructions"""
        return self._settings["custom_instructions"]

    def set_custom_instructions(self, instructions: str) -> None:
        """Set custom instructions"""
        self._settings["custom_instructions"] = instructions
        self.setting_changed.emit("custom_instructions", instructions)

    def get_selected_microphone_id(self) -> str:
        """Get selected microphone device ID"""
        return self._settings["selected_microphone_id"]

    def get_selected_microphone_name(self) -> str:
        """Get selected microphone display name"""
        return self._settings["selected_microphone_name"]

    def set_selected_microphone(self, device_id: str, device_name: str) -> None:
        """Set selected microphone device"""
        self._settings["selected_microphone_id"] = device_id
        self._settings["selected_microphone_name"] = device_name
        self.setting_changed.emit("selected_microphone_id", device_id)
        self.setting_changed.emit("selected_microphone_name", device_name)
        print(f"Microphone updated to: {device_name} (ID: {device_id})")

    def get_all(self) -> dict:
        """Get all settings"""
        return self._settings.copy()

    # Legacy methods for backward compatibility (will be removed after refactor)

    def get_openai_key(self) -> str:
        """Legacy method - get OpenAI API key"""
        return self.get_provider_api_key("openai") or ""

    def set_openai_key(self, key: str) -> None:
        """Legacy method - set OpenAI API key"""
        self.set_provider_api_key("openai", key)
