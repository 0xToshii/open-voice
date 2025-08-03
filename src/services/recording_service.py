from src.interfaces.speech import ISpeechEngine
from src.interfaces.data_store import IDataStore, TranscriptEntry
from src.interfaces.hotkey import IHotkeyHandler
from src.interfaces.text_processing import ITextProcessor
from PySide6.QtCore import QObject, Signal
from datetime import datetime
import time
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
    ):
        super().__init__()

        # Dependency injection
        self.speech_engine = speech_engine
        self.data_store = data_store
        self.hotkey_handler = hotkey_handler
        self.text_processor = text_processor

        # Recording state
        self.is_recording = False
        self.recording_start_time: Optional[float] = None

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

        print("🔴 Recording started")
        self.is_recording = True
        self.recording_start_time = time.time()

        # Emit signal to show recording overlay (thread-safe)
        self.recording_started.emit()

    def stop_recording(self):
        """Stop recording when hotkey is released"""
        if not self.is_recording:
            return

        print("⚫ Recording stopped")
        self.is_recording = False

        # Calculate recording duration
        if self.recording_start_time:
            duration = time.time() - self.recording_start_time
        else:
            duration = 1.0  # Default duration

        # Emit signal to hide recording overlay (thread-safe)
        self.recording_stopped.emit()

        # Process the "recording" (mock for now)
        self.process_recording(duration)

    def process_recording(self, duration: float):
        """Process the completed recording"""
        try:
            # Get transcription from speech engine (mock data for now)
            original_text = self.speech_engine.transcribe(b"mock_audio_data")

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
        """Insert text into the active application (mock for now)"""
        try:
            # TODO: Implement real text insertion using pyautogui/pyperclip
            print(f"📝 Text insertion (mock): '{text}'")

            # Mark insertion as successful
            self.data_store.mark_insertion_status(transcript_id, True)

        except Exception as e:
            print(f"❌ Text insertion failed: {e}")
            self.data_store.mark_insertion_status(transcript_id, False)


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
