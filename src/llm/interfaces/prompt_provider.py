from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class PromptConfig:
    """Configuration for a single prompt in the processing pipeline"""

    name: str
    content: str
    order: int
    enabled: bool = True
    conditional: bool = False  # True for prompts that depend on user settings
    template: bool = (
        False  # True if prompt contains placeholders like {custom_instructions}
    )


class IPromptProvider(ABC):
    """Abstract interface for loading and managing prompts"""

    @abstractmethod
    def get_prompts(self) -> List[PromptConfig]:
        """
        Load all available prompts for the processing pipeline

        Returns:
            List of PromptConfig objects sorted by processing order
        """
        pass

    @abstractmethod
    def reload_prompts(self) -> None:
        """
        Reload prompts from source (useful for development/testing)
        """
        pass

    @abstractmethod
    def get_prompt_by_name(self, name: str) -> PromptConfig:
        """
        Get a specific prompt by name

        Args:
            name: Name of the prompt to retrieve

        Returns:
            PromptConfig object

        Raises:
            KeyError: If prompt with given name doesn't exist
        """
        pass
