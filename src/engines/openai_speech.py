import io
import wave
import tempfile
import os
from typing import Optional
from openai import OpenAI
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager


class OpenAIWhisperEngine(ISpeechEngine):
    """OpenAI Whisper speech recognition engine"""

    def __init__(self, settings_manager: ISettingsManager):
        self.settings_manager = settings_manager
        self.client = None
        self._initialize_client()
        print("🤖 OpenAI Whisper engine initialized")

    def _initialize_client(self):
        """Initialize OpenAI client with API key"""
        try:
            api_key = self.settings_manager.get_openai_key()
            if api_key and api_key.strip():
                self.client = OpenAI(api_key=api_key.strip())
                print("✅ OpenAI client initialized")
            else:
                print("⚠️ No OpenAI API key provided")
                self.client = None
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            self.client = None

    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio data to text using OpenAI Whisper"""
        try:
            if not audio_data:
                return "No audio data received"

            if not self.client:
                self._initialize_client()
                if not self.client:
                    return "OpenAI API key not configured"

            print(f"🔄 Processing {len(audio_data)} bytes with OpenAI Whisper...")

            # Convert raw audio bytes to WAV format for OpenAI
            wav_data = self._bytes_to_wav(audio_data)
            if not wav_data:
                return "Failed to process audio format"

            # Create temporary file for OpenAI API
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(wav_data)
                temp_file_path = temp_file.name

            try:
                # Call OpenAI Whisper API
                with open(temp_file_path, "rb") as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file, response_format="text"
                    )

                text = response.strip() if response else ""

                if text:
                    print(f"✅ OpenAI Whisper transcribed: '{text}'")
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
            print(f"❌ OpenAI Whisper error: {e}")

            # Check for common API errors
            if "Invalid API key" in str(e) or "Unauthorized" in str(e):
                return "Invalid OpenAI API key"
            elif "quota" in str(e).lower():
                return "OpenAI API quota exceeded"
            elif "rate limit" in str(e).lower():
                return "OpenAI API rate limit exceeded"
            else:
                return f"OpenAI error: {str(e)}"

    def is_available(self) -> bool:
        """Check if OpenAI Whisper is available"""
        try:
            api_key = self.settings_manager.get_openai_key()
            if not api_key or not api_key.strip():
                return False

            if not self.client:
                self._initialize_client()

            return self.client is not None

        except Exception as e:
            print(f"❌ OpenAI availability check failed: {e}")
            return False

    def _bytes_to_wav(self, audio_bytes: bytes) -> Optional[bytes]:
        """Convert raw audio bytes to WAV format for OpenAI API"""
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
            print(f"❌ WAV conversion error: {e}")
            return None

    def update_api_key(self, api_key: str):
        """Update the OpenAI API key"""
        self.settings_manager.set_openai_key(api_key)
        self._initialize_client()

    def get_model_info(self) -> dict:
        """Get information about the Whisper model"""
        return {
            "name": "OpenAI Whisper",
            "model": "whisper-1",
            "provider": "OpenAI",
            "accuracy": "High",
            "language_support": "Multilingual",
            "requires_internet": True,
            "requires_api_key": True,
        }
