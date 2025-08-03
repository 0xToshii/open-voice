from abc import ABC, abstractmethod
from typing import Dict, Any


class ITextInserter(ABC):
    """Interface for text insertion implementations"""

    @abstractmethod
    def insert_text(self, text: str) -> bool:
        """
        Insert text into the currently focused application

        Args:
            text: The text to insert

        Returns:
            bool: True if insertion was successful, False otherwise
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this text insertion method is available on the current system

        Returns:
            bool: True if available and functional, False otherwise
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get information about this inserter's capabilities

        Returns:
            dict: Capabilities information including platform, method, features
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name/identifier of this text inserter

        Returns:
            str: Name of the inserter
        """
        pass
