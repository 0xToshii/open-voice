import io
import wave
import numpy as np
from typing import Optional
from faster_whisper import WhisperModel
from src.interfaces.speech import ISpeechEngine
from src.interfaces.settings import ISettingsManager


class LocalWhisperEngine(ISpeechEngine):
    """Local Whisper speech recognition engine using faster-whisper"""

    def __init__(self, settings_manager: ISettingsManager):
        self.settings_manager = settings_manager
        self.model = None
        self.model_size = "base"  # Default model size
        self._initialize_model()
        print("Local Whisper engine initialized")

    def _initialize_model(self):
        """Initialize local Whisper model"""
        try:
            print(f"Loading local Whisper model: {self.model_size}")

            # Initialize faster-whisper model
            # compute_type="int8" for CPU, "float16" for GPU
            self.model = WhisperModel(
                self.model_size, device="cpu", compute_type="int8"
            )

            print(f"Local Whisper model loaded: {self.model_size}")

        except Exception as e:
            print(f"Failed to initialize local Whisper model: {e}")
            self.model = None

    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio data to text using local Whisper"""
        try:
            if not audio_data:
                return "No audio data received"

            if not self.model:
                self._initialize_model()
                if not self.model:
                    return "Local Whisper model not available"

            print(f"Processing {len(audio_data)} bytes with local Whisper...")

            # Convert raw audio bytes to WAV format for Whisper
            wav_data = self._bytes_to_wav(audio_data)
            if not wav_data:
                return "Failed to process audio format"

            # Create temporary file-like object for Whisper
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(wav_data)
                temp_file_path = temp_file.name

            try:
                # Transcribe using local Whisper
                segments, info = self.model.transcribe(
                    temp_file_path,
                    beam_size=5,
                    language=None,  # Auto-detect language
                    condition_on_previous_text=True,
                )

                # Collect all segments
                transcript = ""
                for segment in segments:
                    transcript += segment.text

                text = transcript.strip()

                if text:
                    print(f"Local Whisper transcribed: '{text}'")
                    print(
                        f"   Language: {info.language} (probability: {info.language_probability:.2f})"
                    )
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
            print(f"Local Whisper error: {e}")
            return f"Local Whisper error: {str(e)}"

    def is_available(self) -> bool:
        """Check if local Whisper is available"""
        try:
            # Local Whisper is available if we can load the model
            if self.model is None:
                self._initialize_model()

            return self.model is not None

        except Exception as e:
            print(f"Local Whisper availability check failed: {e}")
            return False

    def _bytes_to_wav(self, audio_bytes: bytes) -> Optional[bytes]:
        """Convert raw audio bytes to WAV format for Whisper"""
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

    def get_model_info(self) -> dict:
        """Get information about the local Whisper model"""
        return {
            "name": "Local Whisper",
            "model": self.model_size,
            "provider": "Local",
            "accuracy": "High",
            "language_support": "Multilingual",
            "requires_internet": False,
            "requires_api_key": False,
        }
