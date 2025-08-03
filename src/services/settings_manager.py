from PySide6.QtCore import QObject, Signal
from src.interfaces.settings import ISettingsManager


class SettingsManager(QObject):
    """Simple in-memory settings manager for API keys implementing ISettingsManager"""

    # Signal emitted when settings change
    setting_changed = Signal(str, str)  # (setting_name, new_value)

    def __init__(self):
        super().__init__()

        # Settings storage (in-memory, no persistence)
        self._settings = {
            "cerebras_key": "",
            "openai_key": "",
            "custom_instructions": "",
        }

    def get_cerebras_key(self) -> str:
        """Get Cerebras API key"""
        return self._settings["cerebras_key"]

    def set_cerebras_key(self, key: str) -> None:
        """Set Cerebras API key"""
        self._settings["cerebras_key"] = key
        self.setting_changed.emit("cerebras_key", key)
        print(f"⚙️ Cerebras key updated: {'*' * min(len(key), 10) if key else 'empty'}")

    def get_openai_key(self) -> str:
        """Get OpenAI API key"""
        return self._settings["openai_key"]

    def set_openai_key(self, key: str) -> None:
        """Set OpenAI API key"""
        self._settings["openai_key"] = key
        self.setting_changed.emit("openai_key", key)
        print(f"⚙️ OpenAI key updated: {'*' * min(len(key), 10) if key else 'empty'}")

    def get_custom_instructions(self) -> str:
        """Get custom instructions"""
        return self._settings["custom_instructions"]

    def set_custom_instructions(self, instructions: str) -> None:
        """Set custom instructions"""
        self._settings["custom_instructions"] = instructions
        self.setting_changed.emit("custom_instructions", instructions)
        print(f"📝 Custom instructions updated: {len(instructions)} characters")
        print(
            f"   Preview: {instructions[:50]}{'...' if len(instructions) > 50 else ''}"
        )

    def get_all(self) -> dict:
        """Get all settings"""
        return self._settings.copy()
