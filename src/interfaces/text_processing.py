from abc import ABC, abstractmethod


class ITextProcessor(ABC):
    """Abstract interface for text processing pipeline"""

    @abstractmethod
    def process_text(self, text: str) -> str:
        """Process transcribed text (future: LLM integration)"""
        pass
