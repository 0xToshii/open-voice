from abc import ABC, abstractmethod
from typing import Callable, List, Dict, Any
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager


class ISpeechEngineFactory(ABC):
    """Abstract interface for speech engine factories"""

    @abstractmethod
    def create_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create a speech engine instance"""
        pass

    @abstractmethod
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about this engine type"""
        pass

    @abstractmethod
    def is_available(self, settings: ISettingsManager) -> bool:
        """Check if this engine is available with current settings"""
        pass


class ISpeechEngineRegistry(ABC):
    """Abstract interface for speech engine registry"""

    @abstractmethod
    def register_engine(
        self, name: str, factory: ISpeechEngineFactory, priority: int = 0
    ) -> None:
        """Register a speech engine factory with priority (higher = preferred)"""
        pass

    @abstractmethod
    def create_best_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create the best available speech engine based on priority and availability"""
        pass

    @abstractmethod
    def create_engine_by_name(
        self, name: str, settings: ISettingsManager
    ) -> ISpeechEngine:
        """Create a specific engine by name"""
        pass

    @abstractmethod
    def get_available_engines(self, settings: ISettingsManager) -> List[Dict[str, Any]]:
        """Get list of available engines with their info"""
        pass

    @abstractmethod
    def get_registered_engines(self) -> List[str]:
        """Get list of all registered engine names"""
        pass


class ISpeechEngineSelector(ABC):
    """Abstract interface for speech engine selection strategy"""

    @abstractmethod
    def select_engine(
        self, registry: ISpeechEngineRegistry, settings: ISettingsManager
    ) -> ISpeechEngine:
        """Select the best speech engine using a specific strategy"""
        pass
