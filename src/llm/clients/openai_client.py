import requests
import json
from typing import Dict, Any
from src.llm.interfaces.llm_client import ILLMClient
from src.interfaces.settings import ISettingsManager


class OpenAILLMClient(ILLMClient):
    """OpenAI LLM client for text processing using GPT-4 mini"""

    def __init__(self, settings_manager: ISettingsManager):
        self.settings_manager = settings_manager
        self.model = "gpt-4o-mini"
        self.api_base_url = "https://api.openai.com/v1"
        self.timeout = 30  # seconds

    def generate(self, system_prompt: str, user_input: str) -> str:
        """Generate response using OpenAI API"""
        if not self.is_available():
            raise Exception("OpenAI client not available - no API key provided")

        api_key = self.settings_manager.get_provider_api_key("openai")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        user_input_prompt = "Transcription input: " + user_input

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input_prompt},
            ],
            "max_tokens": 2048,
            "temperature": 0.1,  # Low temperature for consistent text processing
            "stream": False,
        }

        try:
            print(f"OpenAI LLM: Processing text with {self.model}")
            print(
                f" - System prompt: {system_prompt[:100]}{'...' if len(system_prompt) > 100 else ''}"
            )
            print(f" - Input: {user_input_prompt}")

            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            response_data = response.json()

            if "choices" not in response_data or len(response_data["choices"]) == 0:
                raise Exception("Invalid response format from OpenAI API")

            generated_text = response_data["choices"][0]["message"]["content"].strip()

            print(f" - Output: {generated_text}")

            return generated_text

        except requests.exceptions.RequestException as e:
            print(f"OpenAI API request failed: {e}")
            raise Exception(f"OpenAI API request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"OpenAI API response parsing failed: {e}")
            raise Exception(f"Invalid JSON response from OpenAI API: {e}")
        except Exception as e:
            print(f"OpenAI LLM generation failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if OpenAI client is available"""
        api_key = self.settings_manager.get_provider_api_key("openai")
        return bool(api_key and api_key.strip())

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the OpenAI model"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "api_base": self.api_base_url,
            "max_tokens": 2048,
            "temperature": 0.1,
            "available": self.is_available(),
        }
