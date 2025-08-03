from abc import ABC, abstractmethod
from typing import Callable


class IHotkeyHandler(ABC):
    """Abstract interface for hotkey handling"""

    @abstractmethod
    def register_hotkey(self, on_press: Callable, on_release: Callable) -> None:
        """Register hotkey with press/release callbacks"""
        pass

    @abstractmethod
    def start_listening(self) -> None:
        """Start listening for hotkey events"""
        pass

    @abstractmethod
    def stop_listening(self) -> None:
        """Stop listening for hotkey events"""
        pass
