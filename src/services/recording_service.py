from src.interfaces.speech import ISpeechEngine
from src.interfaces.data_store import IDataStore, TranscriptEntry
from src.interfaces.hotkey import IHotkeyHandler
from src.interfaces.text_processing import ITextProcessor
from src.interfaces.audio_recorder import IAudioRecorder
from src.interfaces.text_insertion import ITextInserter
from src.services.text_inserter_factory import TextInserterFactory
from PySide6.QtCore import QObject, Signal
from datetime import datetime
import time
import subprocess
import platform
from typing import Optional


class VoiceRecordingService(QObject):
    """Main service that coordinates voice recording workflow"""

    # Signals for UI communication (thread-safe)
    transcript_created = Signal(TranscriptEntry)
    recording_started = Signal()
    recording_stopped = Signal()

    def __init__(
        self,
        speech_engine: ISpeechEngine,
        data_store: IDataStore,
        hotkey_handler: IHotkeyHandler,
        text_processor: ITextProcessor,
        audio_recorder: IAudioRecorder,
        text_inserter: Optional[ITextInserter] = None,
    ):
        super().__init__()

        # Dependency injection
        self.speech_engine = speech_engine
        self.data_store = data_store
        self.hotkey_handler = hotkey_handler
        self.text_processor = text_processor
        self.audio_recorder = audio_recorder

        # Text insertion - use provided inserter or create best available
        self.text_inserter = text_inserter or TextInserterFactory.create_best_inserter()

        # Recording state
        self.is_recording = False
        self.recording_start_time: Optional[float] = None
        self.target_app_for_insertion: Optional[str] = None

        # Setup hotkey callbacks
        self.hotkey_handler.register_hotkey(
            on_press=self.start_recording, on_release=self.stop_recording
        )

    def start_service(self):
        """Start the voice recording service"""
        print("Starting Open Voice recording service...")
        self.hotkey_handler.start_listening()
        print("Service started. Press Fn key to record.")

    def stop_service(self):
        """Stop the voice recording service"""
        print("Stopping Open Voice recording service...")
        self.hotkey_handler.stop_listening()

        # Emit signal to hide overlay if recording
        if self.is_recording:
            self.recording_stopped.emit()

        print("Service stopped.")

    def start_recording(self):
        """Start recording when hotkey is pressed"""
        if self.is_recording:
            return

        # CRITICAL: Capture focused app IMMEDIATELY before we do anything else
        self.target_app_for_insertion = self._get_focused_app()
        print(f"🎯 Captured target app for insertion: {self.target_app_for_insertion}")

        print("🔴 Recording started")
        self.is_recording = True
        self.recording_start_time = time.time()

        # Start real audio recording
        self.audio_recorder.start_recording()

        # Emit signal to show recording overlay (thread-safe)
        self.recording_started.emit()

    def _get_focused_app(self) -> Optional[str]:
        """Get the name of the currently focused application"""
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to get name of first application process whose frontmost is true',
                    ],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )

                if result.returncode == 0:
                    app_name = result.stdout.strip()
                    return app_name if app_name else None
                else:
                    print(f"⚠️ Failed to get focused app: {result.stderr}")
                    return None
            else:
                # For non-Mac systems, we can't easily detect focus
                print("⚠️ Focus detection not supported on this platform")
                return None

        except Exception as e:
            print(f"⚠️ Error getting focused app: {e}")
            return None

    def stop_recording(self):
        """Stop recording when hotkey is released"""
        if not self.is_recording:
            return

        print("⚫ Recording stopped")
        self.is_recording = False

        # Stop audio recording and get audio data
        audio_data = self.audio_recorder.stop_recording()

        # Calculate recording duration
        if self.recording_start_time:
            duration = time.time() - self.recording_start_time
        else:
            duration = 1.0  # Default duration

        # Emit signal to hide recording overlay (thread-safe)
        self.recording_stopped.emit()

        # Process the real recording
        self.process_recording(duration, audio_data)

    def process_recording(self, duration: float, audio_data: Optional[bytes] = None):
        """Process the completed recording"""
        try:
            # Get transcription from speech engine using real audio data
            if audio_data:
                print(f"🔄 Processing real audio data ({len(audio_data)} bytes)")
                original_text = self.speech_engine.transcribe(audio_data)
            else:
                print("⚠️ No audio data available, using fallback")
                original_text = "No audio recorded"

            # Process text through pipeline (currently just passthrough)
            processed_text = self.text_processor.process_text(original_text)

            # Save to data store
            transcript_id = self.data_store.save_transcript(
                original_text=original_text,
                processed_text=processed_text,
                duration=duration,
            )

            # Create transcript entry for UI
            entry = TranscriptEntry(
                id=transcript_id,
                original_text=original_text,
                processed_text=processed_text,
                timestamp=datetime.now(),
                duration=duration,
                inserted_successfully=False,
            )

            # Notify UI about new transcript
            self.transcript_created.emit(entry)

            # Simulate text insertion (mock for now)
            self.insert_text(processed_text, transcript_id)

            print(
                f"✅ Transcript created: '{original_text}' (Duration: {duration:.1f}s)"
            )

        except Exception as e:
            print(f"❌ Error processing recording: {e}")

    def insert_text(self, text: str, transcript_id: int):
        """Insert text into the active application using real text insertion"""
        try:
            if not text.strip():
                print("⚠️ Empty text, skipping insertion")
                self.data_store.mark_insertion_status(transcript_id, True)
                return

            print(f"📝 Inserting text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            print(f"🎯 Target app for insertion: {self.target_app_for_insertion}")

            # Use the text inserter with the captured target app
            success = self._insert_text_to_target(text, self.target_app_for_insertion)

            if success:
                print(f"✅ Text insertion successful")
            else:
                print(f"❌ Text insertion failed")

            # Mark insertion status in database
            self.data_store.mark_insertion_status(transcript_id, success)

        except Exception as e:
            print(f"❌ Text insertion error: {e}")
            self.data_store.mark_insertion_status(transcript_id, False)

    def _insert_text_to_target(self, text: str, target_app: Optional[str]) -> bool:
        """Insert text to the specified target app"""
        try:
            if not target_app:
                print("⚠️ No target app captured, using default insertion")
                return self.text_inserter.insert_text(text)

            # Restore focus to target app first
            if self._restore_focus_to_app(target_app):
                # Small delay to ensure focus change takes effect
                time.sleep(0.1)

                # Now insert the text
                return self.text_inserter.insert_text(text)
            else:
                print("⚠️ Failed to restore focus, using fallback insertion")
                return self.text_inserter.insert_text(text)

        except Exception as e:
            print(f"❌ Error in targeted text insertion: {e}")
            return False

    def _restore_focus_to_app(self, app_name: str) -> bool:
        """Restore focus to the specified application"""
        try:
            if not app_name or platform.system() != "Darwin":
                return False

            print(f"🔄 Restoring focus to target app: {app_name}")

            result = subprocess.run(
                ["osascript", "-e", f'tell application "{app_name}" to activate'],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                print(f"✅ Focus restored to {app_name}")
                return True
            else:
                print(f"⚠️ Failed to restore focus to {app_name}: {result.stderr}")
                return False

        except Exception as e:
            print(f"⚠️ Error restoring focus to {app_name}: {e}")
            return False

    def get_text_inserter_info(self) -> dict:
        """Get information about the current text inserter"""
        return self.text_inserter.get_capabilities()

    def set_text_inserter(self, inserter: ITextInserter):
        """Change the text inserter implementation"""
        if inserter and inserter.is_available():
            self.text_inserter = inserter
            capabilities = inserter.get_capabilities()
            print(f"🔧 Text inserter changed to: {capabilities['name']}")
        else:
            print("❌ Cannot set text inserter: not available or invalid")


class MockVoiceRecordingService(QObject):
    """Mock recording service for testing without dependencies"""

    transcript_created = Signal(TranscriptEntry)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.mock_texts = [
            "Hello there. What is your name?",
            "This is a test transcription.",
            "The quick brown fox jumps over the lazy dog.",
            "Testing Open Voice speech recognition.",
            "When I press the hotkey, it should record my voice.",
        ]
        self.text_index = 0

    def start_service(self):
        print("Mock recording service started")

    def stop_service(self):
        print("Mock recording service stopped")

    def simulate_recording(self):
        """Simulate a complete recording cycle"""
        print("🔴 Mock recording started")

        # Get next mock text
        text = self.mock_texts[self.text_index]
        self.text_index = (self.text_index + 1) % len(self.mock_texts)

        # Create mock transcript entry
        entry = TranscriptEntry(
            id=self.text_index,
            original_text=text,
            processed_text=text,
            timestamp=datetime.now(),
            duration=2.5,
            inserted_successfully=True,
        )

        print(f"⚫ Mock recording completed: '{text}'")

        # Emit signal
        self.transcript_created.emit(entry)
