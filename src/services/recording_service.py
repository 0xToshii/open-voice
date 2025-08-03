from src.interfaces.speech_router import ISpeechEngineRouter
from src.interfaces.data_store import IDataStore, TranscriptEntry
from src.interfaces.hotkey import IHotkeyHandler
from src.interfaces.text_processing import ITextProcessor
from src.interfaces.audio_recorder import IAudioRecorder
from src.interfaces.text_insertion import ITextInserter
from src.services.text_inserter_factory import TextInserterFactory
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
        speech_router: ISpeechEngineRouter,
        data_store: IDataStore,
        hotkey_handler: IHotkeyHandler,
        text_processor: ITextProcessor,
        audio_recorder: IAudioRecorder,
        text_inserter: Optional[ITextInserter] = None,
    ):
        super().__init__()

        # Dependency injection - clean abstractions only
        self.speech_router = speech_router
        self.data_store = data_store
        self.hotkey_handler = hotkey_handler
        self.text_processor = text_processor
        self.audio_recorder = audio_recorder

        # Text insertion - use provided inserter or create best available
        self.text_inserter = text_inserter or TextInserterFactory.create_best_inserter()

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

        # Store current focus for Mac-native text insertion
        self._store_focus_if_supported()

        # Start real audio recording
        self.audio_recorder.start_recording()

        # Emit signal to show recording overlay (thread-safe)
        self.recording_started.emit()

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
            # Get transcription using clean speech router (with automatic fallback)
            if audio_data:
                print(f"🔄 Processing real audio data ({len(audio_data)} bytes)")
                original_text = self.speech_router.transcribe_with_fallback(audio_data)

                # Log which engine was actually used
                engine_info = self.speech_router.get_last_used_engine_info()
                if engine_info["success"]:
                    print(
                        f"🎯 Used engine: {engine_info['name']} ({engine_info['provider']})"
                    )
                else:
                    print(
                        f"⚠️ Engine failed: {engine_info.get('error', 'Unknown error')}"
                    )

            else:
                print("⚠️ No audio data available, using fallback")
                original_text = "No audio recorded"

            # Process text through LLM pipeline
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

            # Insert processed text into target application
            self.insert_text(processed_text, transcript_id)

            print(
                f"✅ Transcript created: '{original_text}' (Duration: {duration:.1f}s)"
            )

        except Exception as e:
            print(f"❌ Error processing recording: {e}")

    def _store_focus_if_supported(self):
        """Store current focus if the text inserter supports focus management"""
        try:
            if hasattr(self.text_inserter, "store_current_focus"):
                print("💾 Storing focus before recording...")
                success = self.text_inserter.store_current_focus()
                if success:
                    print("✅ Focus stored successfully")
                else:
                    print(
                        "⚠️ Could not store focus, will use current focus when inserting"
                    )
            else:
                print("ℹ️ Text inserter does not support focus management")
        except Exception as e:
            print(f"❌ Error storing focus: {e}")

    def insert_text(self, text: str, transcript_id: int):
        """Insert text with focus management if supported"""
        try:
            if not text.strip():
                print("⚠️ Empty text, skipping insertion")
                self.data_store.mark_insertion_status(transcript_id, True)
                return

            print(f"📝 Inserting text: '{text[:50]}{'...' if len(text) > 50 else ''}'")

            # Try focus-aware insertion first if supported
            success = False
            if hasattr(self.text_inserter, "insert_text_with_focus_management"):
                print("🎯 Using focus-aware text insertion")
                success = self.text_inserter.insert_text_with_focus_management(text)
            else:
                print("📋 Using standard text insertion")
                success = self.text_inserter.insert_text(text)

            if success:
                print(f"✅ Text insertion successful")
            else:
                print(f"❌ Text insertion failed")

            # Mark insertion status in database
            self.data_store.mark_insertion_status(transcript_id, success)

        except Exception as e:
            print(f"❌ Text insertion error: {e}")
            self.data_store.mark_insertion_status(transcript_id, False)

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

    def get_speech_router_info(self) -> dict:
        """Get information about the speech router and available engines"""
        try:
            available_engines = self.speech_router.get_available_engines()
            last_used = self.speech_router.get_last_used_engine_info()

            return {
                "available_engines": available_engines,
                "last_used_engine": last_used,
                "router_available": self.speech_router.is_available(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "available_engines": [],
                "last_used_engine": None,
                "router_available": False,
            }

    def get_audio_recorder(self) -> IAudioRecorder:
        """Get the audio recorder instance for real-time level monitoring"""
        return self.audio_recorder


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
