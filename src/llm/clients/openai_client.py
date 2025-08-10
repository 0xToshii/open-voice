import requests
import json
from typing import Dict, Any
from src.llm.interfaces.llm_client import ILLMClient
from src.interfaces.settings import ISettingsManager


class OpenAILLMClient(ILLMClient):
    """OpenAI LLM client for text processing"""

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
            "temperature": 0,  # Low temperature for consistent text processing
            "stream": False,
            "response_format": {"type": "json_object"},  #
        }

        try:
            print(f"OpenAI LLM: Processing text with {self.model}")
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

            json_content = response_data["choices"][0]["message"]["content"].strip()

            try:
                # Parse the JSON response
                json_content = json_content.replace("```json", "").replace("```", "")
                parsed_response = json.loads(json_content)

                # Log thoughts for debugging/monitoring
                if "thoughts" in parsed_response:
                    print(f" - Thoughts: {parsed_response['thoughts']}")

                # Extract the output field
                if "output" in parsed_response:
                    output_text = parsed_response["output"]
                    print(f" - Output: {output_text}")
                    return output_text
                else:
                    print(
                        "No 'output' field in JSON response, returning original input"
                    )
                    return user_input

            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Raw response: {json_content}")
                # Return original input as fallback
                return user_input

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
            "available": self.is_available(),
        }
