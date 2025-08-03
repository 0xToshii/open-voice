from typing import Dict, List, Tuple, Any
from src.interfaces.speech_factory import ISpeechEngineFactory, ISpeechEngineRegistry
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager


class SpeechEngineRegistry(ISpeechEngineRegistry):
    """Registry for managing speech engine factories with priority-based selection"""

    def __init__(self):
        # Store as (factory, priority) tuples, sorted by priority descending
        self._engines: Dict[str, Tuple[ISpeechEngineFactory, int]] = {}

    def register_engine(
        self, name: str, factory: ISpeechEngineFactory, priority: int = 0
    ) -> None:
        """Register a speech engine factory with priority (higher = preferred)"""
        if not isinstance(factory, ISpeechEngineFactory):
            raise ValueError(f"Factory must implement ISpeechEngineFactory interface")

        self._engines[name] = (factory, priority)
        print(f"🔧 Registered speech engine: {name} (priority: {priority})")

    def create_best_engine(self, settings: ISettingsManager) -> ISpeechEngine:
        """Create the best available speech engine based on priority and availability"""
        if not self._engines:
            raise RuntimeError("No speech engines registered")

        # Sort by priority (highest first)
        sorted_engines = sorted(
            self._engines.items(),
            key=lambda x: x[1][1],  # Sort by priority
            reverse=True,
        )

        for name, (factory, priority) in sorted_engines:
            try:
                if factory.is_available(settings):
                    print(f"🚀 Selected speech engine: {name} (priority: {priority})")
                    return factory.create_engine(settings)
                else:
                    print(f"⚠️ Engine {name} not available")
            except Exception as e:
                print(f"⚠️ Failed to create engine {name}: {e}")

        # If no engines are available, raise an error
        raise RuntimeError("No speech engines are available")

    def create_engine_by_name(
        self, name: str, settings: ISettingsManager
    ) -> ISpeechEngine:
        """Create a specific engine by name"""
        if name not in self._engines:
            available_engines = list(self._engines.keys())
            raise ValueError(
                f"Engine '{name}' not registered. Available: {available_engines}"
            )

        factory, _ = self._engines[name]

        if not factory.is_available(settings):
            raise RuntimeError(
                f"Engine '{name}' is not available with current settings"
            )

        return factory.create_engine(settings)

    def get_available_engines(self, settings: ISettingsManager) -> List[Dict[str, Any]]:
        """Get list of available engines with their info"""
        available_engines = []

        for name, (factory, priority) in self._engines.items():
            try:
                engine_info = factory.get_engine_info().copy()
                engine_info.update(
                    {"available": factory.is_available(settings), "priority": priority}
                )
                available_engines.append(engine_info)
            except Exception as e:
                available_engines.append(
                    {
                        "name": name,
                        "id": name,
                        "available": False,
                        "priority": priority,
                        "error": str(e),
                    }
                )

        # Sort by priority for consistent ordering
        available_engines.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return available_engines

    def get_registered_engines(self) -> List[str]:
        """Get list of all registered engine names"""
        return list(self._engines.keys())

    def unregister_engine(self, name: str) -> bool:
        """Unregister an engine by name"""
        if name in self._engines:
            del self._engines[name]
            print(f"🗑️ Unregistered speech engine: {name}")
            return True
        return False

    def is_engine_registered(self, name: str) -> bool:
        """Check if an engine is registered"""
        return name in self._engines

    def get_engine_priority(self, name: str) -> int:
        """Get the priority of a registered engine"""
        if name not in self._engines:
            raise ValueError(f"Engine '{name}' not registered")
        return self._engines[name][1]

    def update_engine_priority(self, name: str, priority: int) -> None:
        """Update the priority of a registered engine"""
        if name not in self._engines:
            raise ValueError(f"Engine '{name}' not registered")

        factory, _ = self._engines[name]
        self._engines[name] = (factory, priority)
        print(f"🔧 Updated {name} priority to {priority}")
