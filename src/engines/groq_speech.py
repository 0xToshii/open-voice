import io
import wave
import tempfile
import os
from typing import Optional
from groq import Groq
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager


class GroqSpeechEngine(ISpeechEngine):
    """Groq speech recognition engine"""

    def __init__(self, settings_manager: ISettingsManager):
        self.settings_manager = settings_manager
        self.client = None
        self._initialize_client()
        print("Groq speech engine initialized")

    def _initialize_client(self):
        """Initialize Groq client with API key"""
        try:
            api_key = self.settings_manager.get_provider_api_key("groq")
            if api_key and api_key.strip():
                self.client = Groq(api_key=api_key.strip())
                print("Groq client initialized")
            else:
                print("No Groq API key provided")
                self.client = None
        except Exception as e:
            print(f"Failed to initialize Groq client: {e}")
            self.client = None

    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio data to text using Groq Whisper"""
        try:
            if not audio_data:
                return "No audio data received"

            if not self.client:
                self._initialize_client()
                if not self.client:
                    return "Groq API key not configured"

            print(f"Processing {len(audio_data)} bytes with Groq Whisper...")

            # Convert raw audio bytes to WAV format for Groq
            wav_data = self._bytes_to_wav(audio_data)
            if not wav_data:
                return "Failed to process audio format"

            # Create temporary file for Groq API
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(wav_data)
                temp_file_path = temp_file.name

            try:
                # Call Groq Whisper API
                with open(temp_file_path, "rb") as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=audio_file,
                        response_format="text",
                    )

                text = response.strip() if response else ""

                if text:
                    print(f"Groq Whisper transcribed: '{text}'")
                    return text
                else:
                    return "Could not understand audio"

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except Exception as e:
            print(f"Groq Whisper error: {e}")

            # Check for common API errors
            if "Invalid API key" in str(e) or "Unauthorized" in str(e):
                return "Invalid Groq API key"
            elif "quota" in str(e).lower():
                return "Groq API quota exceeded"
            elif "rate limit" in str(e).lower():
                return "Groq API rate limit exceeded"
            else:
                return f"Groq error: {str(e)}"

    def is_available(self) -> bool:
        """Check if Groq Whisper is available"""
        try:
            api_key = self.settings_manager.get_provider_api_key("groq")
            if not api_key or not api_key.strip():
                return False

            if not self.client:
                self._initialize_client()

            return self.client is not None

        except Exception as e:
            print(f"Groq availability check failed: {e}")
            return False

    def _bytes_to_wav(self, audio_bytes: bytes) -> Optional[bytes]:
        """Convert raw audio bytes to WAV format for Groq API"""
        try:
            # Audio parameters (matching our recorder settings)
            sample_rate = 16000
            sample_width = 2  # 16-bit = 2 bytes
            channels = 1  # Mono

            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_bytes)

            # Get WAV data
            wav_data = wav_buffer.getvalue()
            return wav_data

        except Exception as e:
            print(f"WAV conversion error: {e}")
            return None

    def update_api_key(self, api_key: str):
        """Update the Groq API key"""
        self.settings_manager.set_provider_api_key("groq", api_key)
        self._initialize_client()

    def get_model_info(self) -> dict:
        """Get information about the speech model"""
        return {
            "name": "Groq Speech",
            "model": "whisper-large-v3",
            "provider": "Groq",
            "requires_internet": True,
            "requires_api_key": True,
        }
