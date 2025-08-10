from typing import Dict, Any
from src.llm.interfaces.llm_client import ILLMClient


class PassthroughLLMClient(ILLMClient):
    """Production fallback LLM client that returns input unchanged when LLM services unavailable"""

    def __init__(self):
        self.call_count = 0

    def generate(self, system_prompt: str, user_input: str) -> str:
        """Return user input as-is (passthrough when LLM unavailable)"""
        self.call_count += 1

        print(f"Passthrough LLM: Call #{self.call_count} (returning input unchanged)")
        print(f"   Input: {user_input}")
        print(f"   Output: {user_input}")

        return user_input

    def is_available(self) -> bool:
        """Passthrough is always available as fallback"""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get passthrough model information"""
        return {
            "provider": "Passthrough",
            "model": "passthrough-fallback-v1",
            "api_base": "none",
            "available": True,
            "purpose": "production_fallback",
            "call_count": self.call_count,
        }
