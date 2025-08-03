import sounddevice as sd
import numpy as np
import threading
import queue
import time
from typing import Optional
from src.interfaces.audio_recorder import IAudioRecorder


class PyAudioRecorder(IAudioRecorder):
    """Real audio recorder using sounddevice for microphone capture"""

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = 1024  # Audio buffer size

        # Recording state
        self._is_recording = False
        self._recording_thread: Optional[threading.Thread] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._audio_buffer: list = []
        self._current_level: float = 0.0
        self._level_lock = threading.Lock()

        # Audio stream
        self._stream: Optional[sd.InputStream] = None

        # Debug: Show available audio devices
        self._print_audio_devices()

    def _print_audio_devices(self):
        """Debug: Print all available audio devices"""
        try:
            print("\n🔍 Available Audio Devices:")
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                device_type = ""
                if device["max_inputs"] > 0:
                    device_type += "INPUT "
                if device["max_outputs"] > 0:
                    device_type += "OUTPUT"

                default_marker = ""
                if i == sd.default.device[0]:  # Default input
                    default_marker = " ← DEFAULT INPUT"
                elif i == sd.default.device[1]:  # Default output
                    default_marker = " ← DEFAULT OUTPUT"

                print(f"  {i}: {device['name']} ({device_type}){default_marker}")

            # Show which device we'll use
            default_input = (
                sd.default.device[0]
                if isinstance(sd.default.device, (list, tuple))
                else sd.default.device
            )
            print(f"🎤 Will use device: {default_input}\n")

        except Exception as e:
            print(f"❌ Error listing audio devices: {e}")

    def start_recording(self) -> None:
        """Start audio recording from microphone"""
        if self._is_recording:
            return

        print("🎤 Starting real audio recording...")
        self._is_recording = True
        self._audio_buffer = []

        try:
            # Create audio input stream
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
            )

            # Start the stream
            self._stream.start()
            print(
                f"✅ Audio stream started: {self.sample_rate}Hz, {self.channels} channel(s)"
            )

        except Exception as e:
            print(f"❌ Failed to start audio recording: {e}")
            self._is_recording = False
            if self._stream:
                self._stream.close()
                self._stream = None

    def stop_recording(self) -> Optional[bytes]:
        """Stop recording and return audio data as bytes"""
        if not self._is_recording:
            return None

        print("🛑 Stopping audio recording...")
        self._is_recording = False

        try:
            # Stop and close stream
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            # Collect all audio data
            if not self._audio_buffer:
                print("⚠️ No audio data recorded")
                return None

            # Convert audio buffer to numpy array
            audio_data = np.concatenate(self._audio_buffer, axis=0)

            # Debug: Analyze raw audio data
            self._analyze_audio_data(audio_data)

            # Normalize and convert to 16-bit PCM
            audio_normalized = self._normalize_audio(audio_data)
            audio_int16 = (audio_normalized * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()

            duration = len(audio_data) / self.sample_rate
            print(
                f"✅ Audio recording completed: {duration:.2f}s, {len(audio_bytes)} bytes"
            )

            # Debug: Save WAV file for manual inspection
            self._save_debug_wav(audio_bytes, duration)

            return audio_bytes

        except Exception as e:
            print(f"❌ Error stopping audio recording: {e}")
            return None

    def _analyze_audio_data(self, audio_data: np.ndarray) -> None:
        """Debug: Analyze captured audio data"""
        try:
            # Flatten to 1D if needed
            if audio_data.ndim > 1:
                audio_flat = audio_data.flatten()
            else:
                audio_flat = audio_data

            # Calculate statistics
            min_val = float(np.min(audio_flat))
            max_val = float(np.max(audio_flat))
            rms = float(np.sqrt(np.mean(audio_flat**2)))
            peak = float(np.max(np.abs(audio_flat)))

            print(f"🔍 Audio Analysis:")
            print(f"   Min: {min_val:.6f}, Max: {max_val:.6f}")
            print(f"   RMS: {rms:.6f}, Peak: {peak:.6f}")
            print(f"   Samples: {len(audio_flat)}")

            # Check if we have actual audio content
            if rms < 0.001:
                print("⚠️ WARNING: Audio RMS very low - might be silence/noise")
            elif rms > 0.1:
                print("✅ Good audio levels detected")
            else:
                print("⚠️ Audio levels seem low but present")

        except Exception as e:
            print(f"❌ Error analyzing audio: {e}")

    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio data to prevent clipping and improve recognition"""
        try:
            # Flatten to 1D if needed
            if audio_data.ndim > 1:
                audio_flat = audio_data.flatten()
            else:
                audio_flat = audio_data.copy()

            # Remove DC offset
            audio_flat = audio_flat - np.mean(audio_flat)

            # Get peak amplitude
            peak = np.max(np.abs(audio_flat))

            if peak > 0:
                # Normalize to 70% of maximum to prevent clipping
                audio_flat = audio_flat * (0.7 / peak)
                print(
                    f"🔧 Audio normalized: peak was {peak:.4f}, now {np.max(np.abs(audio_flat)):.4f}"
                )
            else:
                print("⚠️ Audio peak is zero - no normalization applied")

            return audio_flat

        except Exception as e:
            print(f"❌ Error normalizing audio: {e}")
            return audio_data

    def _save_debug_wav(self, audio_bytes: bytes, duration: float) -> None:
        """Debug: Save WAV file for manual inspection"""
        try:
            import wave
            import os

            # Create debug directory if it doesn't exist
            debug_dir = "debug/debug_audio"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)

            # Generate filename with timestamp
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            wav_file_path = f"{debug_dir}/recording_{timestamp}.wav"

            # Write WAV file
            with wave.open(wav_file_path, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit = 2 bytes
                wav_file.setframerate(self.sample_rate)  # 16kHz
                wav_file.writeframes(audio_bytes)

            print(f"💾 Debug WAV saved: {wav_file_path} ({duration:.2f}s)")
            print(f"   You can play this file to verify audio quality")

        except Exception as e:
            print(f"❌ Error saving debug WAV: {e}")

    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._is_recording

    def get_audio_level(self) -> float:
        """Get current audio level for visualization (0.0 to 1.0)"""
        with self._level_lock:
            return self._current_level

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info, status
    ) -> None:
        """Callback function for audio stream (runs on audio thread)"""
        if not self._is_recording:
            return

        try:
            # Store audio data
            self._audio_buffer.append(indata.copy())

            # Calculate audio level for visualization
            if len(indata) > 0:
                # Calculate RMS (root mean square) level
                rms = np.sqrt(np.mean(indata**2))
                # Normalize to 0-1 range (assuming max RMS of ~0.1 for normal speech)
                level = min(rms * 10, 1.0)

                with self._level_lock:
                    self._current_level = level

        except Exception as e:
            print(f"❌ Audio callback error: {e}")

    def get_audio_info(self) -> dict:
        """Get audio recording configuration info"""
        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size,
            "is_recording": self._is_recording,
            "buffer_size": len(self._audio_buffer) if self._audio_buffer else 0,
        }


class MockAudioRecorder(IAudioRecorder):
    """Mock audio recorder for testing without microphone"""

    def __init__(self):
        self._is_recording = False
        self._start_time: Optional[float] = None
        self._mock_level = 0.0

    def start_recording(self) -> None:
        """Mock start recording"""
        self._is_recording = True
        self._start_time = time.time()
        print("🎤 Mock audio recording started")

    def stop_recording(self) -> Optional[bytes]:
        """Mock stop recording with fake audio data"""
        if not self._is_recording:
            return None

        self._is_recording = False
        duration = time.time() - self._start_time if self._start_time else 1.0

        # Generate fake audio data (silence)
        sample_rate = 16000
        samples = int(duration * sample_rate)
        fake_audio = np.zeros(samples, dtype=np.int16)

        print(f"🎤 Mock audio recording completed: {duration:.2f}s")
        return fake_audio.tobytes()

    def is_recording(self) -> bool:
        """Check if mock recording"""
        return self._is_recording

    def get_audio_level(self) -> float:
        """Get mock audio level"""
        if self._is_recording:
            # Simulate fluctuating audio level
            import random

            self._mock_level = random.uniform(0.2, 0.8)
        else:
            self._mock_level = 0.0
        return self._mock_level
