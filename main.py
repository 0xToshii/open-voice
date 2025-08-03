#!/usr/bin/env python3
"""
Open Voice - Speech-to-Text Mac Application
Main entry point with complete recording flow
"""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.data.mock_data_store import MockDataStore
from src.engines.speech_factory import SpeechEngineFactory
from src.services.audio_recorder import PyAudioRecorder, MockAudioRecorder
from src.services.hotkey_handler import FnKeyHandler, MockHotkeyHandler
from src.services.text_processor import TextProcessor
from src.services.recording_service import VoiceRecordingService
from src.services.settings_manager import SettingsManager


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Open Voice")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Open Voice")

    # Create dependencies using dependency injection
    data_store = MockDataStore()
    text_processor = TextProcessor()

    # Create settings manager first (needed for speech engine)
    settings_manager = SettingsManager()

    # Use speech engine factory to get best available engine
    speech_engine = SpeechEngineFactory.create_best_engine(settings_manager)

    # Try to use real audio recorder, fallback to mock if microphone issues
    try:
        audio_recorder = PyAudioRecorder()
        print("✅ Using real audio recorder")
    except Exception as e:
        print(f"⚠️ Falling back to mock audio recorder: {e}")
        audio_recorder = MockAudioRecorder()

    # Try to use real hotkey handler, fallback to mock if permissions issue
    try:
        hotkey_handler = FnKeyHandler()
        print("✅ Using real hotkey detection")
    except Exception as e:
        print(f"⚠️ Falling back to mock hotkey handler: {e}")
        hotkey_handler = MockHotkeyHandler()

    # Create recording service with all dependencies
    recording_service = VoiceRecordingService(
        speech_engine=speech_engine,
        data_store=data_store,
        hotkey_handler=hotkey_handler,
        text_processor=text_processor,
        audio_recorder=audio_recorder,
    )

    # Create and show main window with dependency injection
    window = MainWindow(data_store, settings_manager, recording_service)
    window.show()

    # Start the recording service
    recording_service.start_service()

    # Add instructions for testing
    print("\n🎤 Open Voice is running!")
    print("📝 Instructions:")
    if isinstance(hotkey_handler, MockHotkeyHandler):
        print("   - This is using mock hotkey detection")
        print(
            "   - Use the console to test: hotkey_handler.simulate_press() then hotkey_handler.simulate_release()"
        )
    else:
        print("   - Press and hold Cmd+Shift+Space to record")
        print("   - Alternative: Press F13 key (if available)")
        print("   - Release keys to stop recording and add transcript")
    print("   - Check the History tab to see new transcripts appear")
    print("   - Press Ctrl+C to quit\n")

    try:
        # Start the application event loop
        result = app.exec()
    finally:
        # Clean shutdown
        recording_service.stop_service()

    return result


if __name__ == "__main__":
    sys.exit(main())
