import requests
import json
from typing import Dict, Any
from src.llm.interfaces.llm_client import ILLMClient
from src.interfaces.settings import ISettingsManager


class CerebrasLLMClient(ILLMClient):
    """Cerebras LLM client for text processing using llama-4-maverick-17b-128e-instruct"""

    def __init__(self, settings_manager: ISettingsManager):
        self.settings_manager = settings_manager
        self.model = "llama-4-maverick-17b-128e-instruct"
        self.api_base_url = "https://api.cerebras.ai/v1"
        self.timeout = 30  # seconds

    def generate(self, system_prompt: str, user_input: str) -> str:
        """Generate response using Cerebras API"""
        if not self.is_available():
            raise Exception("Cerebras client not available - no API key provided")

        api_key = self.settings_manager.get_cerebras_key()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            "max_tokens": 2048,
            "temperature": 0.1,  # Low temperature for consistent text processing
            "stream": False,
        }

        try:
            print(f"🧠 Cerebras LLM: Processing text with {self.model}")
            print(
                f"   System prompt: {system_prompt[:100]}{'...' if len(system_prompt) > 100 else ''}"
            )
            print(
                f"   Input: {user_input[:100]}{'...' if len(user_input) > 100 else ''}"
            )

            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            response_data = response.json()

            if "choices" not in response_data or len(response_data["choices"]) == 0:
                raise Exception("Invalid response format from Cerebras API")

            generated_text = response_data["choices"][0]["message"]["content"].strip()

            print(
                f"   Output: {generated_text[:100]}{'...' if len(generated_text) > 100 else ''}"
            )

            return generated_text

        except requests.exceptions.RequestException as e:
            print(f"❌ Cerebras API request failed: {e}")
            raise Exception(f"Cerebras API request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ Cerebras API response parsing failed: {e}")
            raise Exception(f"Invalid JSON response from Cerebras API: {e}")
        except Exception as e:
            print(f"❌ Cerebras LLM generation failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if Cerebras client is available"""
        api_key = self.settings_manager.get_cerebras_key()
        return bool(api_key and api_key.strip())

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Cerebras model"""
        return {
            "provider": "Cerebras",
            "model": self.model,
            "api_base": self.api_base_url,
            "max_tokens": 2048,
            "temperature": 0.1,
            "available": self.is_available(),
        }


class MockLLMClient(ILLMClient):
    """Mock LLM client for testing without API calls"""

    def __init__(self):
        self.call_count = 0

    def generate(self, system_prompt: str, user_input: str) -> str:
        """Return mock processed text"""
        self.call_count += 1

        print(f"🧠 Mock LLM: Call #{self.call_count}")
        print(
            f"   System prompt: {system_prompt[:50]}{'...' if len(system_prompt) > 50 else ''}"
        )
        print(f"   Input: {user_input}")

        # Simple mock processing - just add a tag to show it was processed
        if "grammar" in system_prompt.lower():
            result = f"{user_input.strip().capitalize()}."
        elif "style" in system_prompt.lower():
            result = user_input.replace("um", "").replace("uh", "").strip()
        elif "custom" in system_prompt.lower():
            result = user_input.lower()  # Mock custom instruction: make lowercase
        else:
            result = f"[LLM-{self.call_count}] {user_input.strip()}"

        print(f"   Output: {result}")
        return result

    def is_available(self) -> bool:
        """Mock is always available"""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information"""
        return {
            "provider": "Mock",
            "model": "mock-llm-v1",
            "api_base": "mock://localhost",
            "available": True,
            "call_count": self.call_count,
        }
