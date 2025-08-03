from src.interfaces.text_processing import ITextProcessor


class TextProcessor(ITextProcessor):
    """Text processor for handling transcript post-processing"""

    def __init__(self):
        # Future: Initialize LLM client here
        pass

    def process_text(self, text: str) -> str:
        """Process transcribed text (currently passthrough, future: LLM integration)"""
        # For now, just return the text as-is
        # Future implementation will include:
        # - LLM processing for commands like "scratch that part"
        # - Text cleaning and formatting
        # - Grammar correction

        return text.strip()


class MockTextProcessor(ITextProcessor):
    """Mock text processor for testing"""

    def process_text(self, text: str) -> str:
        """Mock processing - just add a prefix to show it was processed"""
        return f"[Processed] {text.strip()}"
