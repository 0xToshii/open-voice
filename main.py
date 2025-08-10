#!/usr/bin/env python3
"""
Open Voice - Speech-to-Text Mac Application
Main entry point with complete recording flow
"""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.services.di_container import DIContainer
from src.services.hotkey_handler import MockHotkeyHandler


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Open Voice")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Open Voice")

    # Create dependency injection container
    container = DIContainer()

    # Configure for production use (real audio/hotkey handlers)
    # For testing, call: container.configure_for_testing()

    # Initialize all critical services for optimal performance
    container.init_critical_services()

    # Get all dependencies from container (these will now be cached)
    data_store = container.get_data_store()
    settings_manager = container.get_settings_manager()
    recording_service = container.get_recording_service()

    # Create and show main window with dependency injection
    window = MainWindow(data_store, settings_manager, recording_service)
    window.show()

    # Start the recording service
    recording_service.start_service()

    # Add instructions for testing
    print("\n🎤 Open Voice is running!")
    print("📝 Instructions:")
    hotkey_handler = container.get_hotkey_handler()
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
