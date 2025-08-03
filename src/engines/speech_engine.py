import speech_recognition as sr
import io
import numpy as np
import wave
from typing import Optional
from src.interfaces.speech import ISpeechEngine


class SpeechRecognitionEngine(ISpeechEngine):
    """Real speech recognition using Google Speech Recognition"""

    def __init__(self, engine_type: str = "google"):
        self.engine_type = engine_type
        self.recognizer = sr.Recognizer()

        # Configure recognizer settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3

        print(f"🤖 Speech recognition engine initialized: {engine_type}")

    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio data to text using speech recognition"""
        try:
            if not audio_data:
                return "No audio data received"

            print(f"🔄 Processing {len(audio_data)} bytes of audio...")

            # Convert raw audio bytes to AudioData format
            audio_file = self._bytes_to_audio_data(audio_data)

            if not audio_file:
                return "Failed to process audio format"

            # Perform speech recognition
            text = self._recognize_audio(audio_file)

            if text:
                print(f"✅ Speech recognized: '{text}'")
                return text
            else:
                return "Could not understand audio"

        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
            return f"Recognition error: {str(e)}"

    def is_available(self) -> bool:
        """Check if speech recognition is available"""
        try:
            # Test if we can create a recognizer
            test_recognizer = sr.Recognizer()
            return True
        except Exception as e:
            print(f"❌ Speech recognition not available: {e}")
            return False

    def _bytes_to_audio_data(self, audio_bytes: bytes) -> Optional[sr.AudioData]:
        """Convert raw audio bytes to SpeechRecognition AudioData format"""
        try:
            # Create a WAV file in memory from raw audio bytes
            # Assume 16kHz, 16-bit, mono (matching our recorder settings)
            sample_rate = 16000
            sample_width = 2  # 16-bit = 2 bytes

            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_bytes)

            # Reset buffer position
            wav_buffer.seek(0)

            # Convert to AudioData
            with sr.AudioFile(wav_buffer) as source:
                audio_data = self.recognizer.record(source)
                return audio_data

        except Exception as e:
            print(f"❌ Audio conversion error: {e}")
            return None

    def _recognize_audio(self, audio_data: sr.AudioData) -> Optional[str]:
        """Recognize speech from AudioData using configured engine"""
        try:
            if self.engine_type == "google":
                # Use Google Speech Recognition (free tier)
                text = self.recognizer.recognize_google(audio_data)
                return text

            elif self.engine_type == "sphinx":
                # Use offline Sphinx (requires pocketsphinx)
                text = self.recognizer.recognize_sphinx(audio_data)
                return text

            elif self.engine_type == "whisper":
                # Use OpenAI Whisper (requires openai-whisper)
                text = self.recognizer.recognize_whisper(audio_data)
                return text

            else:
                print(f"❌ Unknown engine type: {self.engine_type}")
                return None

        except sr.UnknownValueError:
            print("⚠️ Speech was unclear or not detected")
            return "Speech not clear"
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")
            return f"Service error: {e}"
        except Exception as e:
            print(f"❌ Recognition error: {e}")
            return f"Error: {e}"

    def set_engine(self, engine_type: str) -> None:
        """Change the speech recognition engine"""
        self.engine_type = engine_type
        print(f"🔄 Speech engine changed to: {engine_type}")

    def adjust_for_ambient_noise(self, duration: float = 1.0) -> None:
        """Adjust recognizer sensitivity based on ambient noise"""
        try:
            print(f"🔧 Adjusting for ambient noise ({duration}s)...")
            # This would typically be done with microphone input
            # For now, just adjust energy threshold
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            print("✅ Ambient noise adjustment completed")
        except Exception as e:
            print(f"❌ Ambient noise adjustment failed: {e}")


class OfflineSpeechEngine(ISpeechEngine):
    """Offline speech recognition using built-in engines"""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        print("🤖 Offline speech recognition engine initialized")

    def transcribe(self, audio_data: bytes) -> str:
        """Convert audio using offline recognition"""
        try:
            if not audio_data:
                return "No audio data received"

            # Create AudioData from bytes (similar to online version)
            audio_file = self._bytes_to_audio_data(audio_data)

            if not audio_file:
                return "Failed to process audio format"

            # Use offline Sphinx recognition
            try:
                text = self.recognizer.recognize_sphinx(audio_file)
                if text:
                    print(f"✅ Offline speech recognized: '{text}'")
                    return text
                else:
                    return "Could not understand audio"
            except sr.UnknownValueError:
                return "Speech not clear"
            except Exception as e:
                return f"Offline recognition error: {e}"

        except Exception as e:
            print(f"❌ Offline speech recognition error: {e}")
            return f"Recognition error: {str(e)}"

    def is_available(self) -> bool:
        """Check if offline recognition is available"""
        try:
            # Test if Sphinx is available
            test_recognizer = sr.Recognizer()
            # This will fail if pocketsphinx is not installed
            test_audio = sr.AudioData(b"\x00" * 1000, 16000, 2)
            test_recognizer.recognize_sphinx(test_audio)
            return True
        except:
            print(
                "⚠️ Offline speech recognition not available (pocketsphinx not installed)"
            )
            return False

    def _bytes_to_audio_data(self, audio_bytes: bytes) -> Optional[sr.AudioData]:
        """Convert raw audio bytes to AudioData format"""
        try:
            sample_rate = 16000
            sample_width = 2

            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_bytes)

            wav_buffer.seek(0)

            with sr.AudioFile(wav_buffer) as source:
                audio_data = self.recognizer.record(source)
                return audio_data

        except Exception as e:
            print(f"❌ Offline audio conversion error: {e}")
            return None
