from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QFont
from src.ui.audio_waveform import AudioWaveformWidget
from typing import Optional, Any
import sys


class RecordingOverlay(QWidget):
    """Recording overlay that appears at the bottom of the screen"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.is_recording = False

    def setup_ui(self):
        """Setup the overlay UI"""
        # Make the widget frameless and always on top, but never steal focus
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

        # Ensure overlay doesn't activate when shown
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Set size and position for waveform only
        self.setFixedSize(200, 50)  # Smaller since no text
        self.center_at_bottom()

        # Setup main layout - just for waveform
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # No padding for perfect centering

        # Audio waveform widget (centered)
        self.waveform = AudioWaveformWidget(bar_count=10)  # Fewer bars for better fit
        self.waveform.setObjectName("audioWaveform")

        # Center the waveform perfectly
        main_layout.addStretch()
        main_layout.addWidget(self.waveform)
        main_layout.addStretch()

        self.setLayout(main_layout)

        # Apply styles
        self.apply_styles()

        # Start hidden
        self.hide()

        # Track audio recorder for real-time updates
        self.audio_recorder: Optional[Any] = None
        self.audio_update_timer = QTimer()
        self.audio_update_timer.timeout.connect(self.update_audio_levels)
        self.audio_update_timer.setInterval(33)  # ~30fps for audio level updates

    def center_at_bottom(self):
        """Position the overlay at the bottom center of the screen"""
        # Get screen geometry
        screen = self.screen()
        if screen:
            screen_rect = screen.availableGeometry()
            x = (screen_rect.width() - self.width()) // 2
            y = screen_rect.height() - self.height() - 50  # 50px from bottom
            self.move(x, y)

    def set_audio_recorder(self, audio_recorder):
        """Set the audio recorder for real-time level updates"""
        self.audio_recorder = audio_recorder

    def show_recording(self):
        """Show the recording overlay with waveform animation"""
        if self.is_recording:
            return

        self.is_recording = True
        self.center_at_bottom()  # Ensure proper positioning
        self.show()
        self.raise_()  # Bring to front

        # Start waveform animation
        self.waveform.start_animation()

        # Start audio level updates
        self.audio_update_timer.start()

    def hide_recording(self):
        """Hide the recording overlay"""
        if not self.is_recording:
            return

        self.is_recording = False

        # Stop animations
        self.audio_update_timer.stop()
        self.waveform.stop_animation()

        self.hide()

    def update_audio_levels(self):
        """Update waveform with real-time audio levels"""
        if self.audio_recorder and self.is_recording:
            try:
                level = self.audio_recorder.get_audio_level()
                self.waveform.update_audio_level(level)
            except Exception as e:
                # Fallback to mock levels if audio recorder fails
                import random

                mock_level = random.uniform(0.1, 0.7)
                self.waveform.update_audio_level(mock_level)

    def apply_styles(self):
        """Apply CSS styles to the overlay"""
        style = """
        QWidget {
            background-color: rgb(10, 10, 10);
            border-radius: 25px;
            border: none;
        }
        """

        self.setStyleSheet(style)


class MockRecordingOverlay(QWidget):
    """Mock recording overlay for testing without screen overlay"""

    def __init__(self):
        super().__init__()
        self.is_recording = False

    def show_recording(self):
        """Mock show recording"""
        self.is_recording = True
        print("🔴 Recording overlay shown")

    def hide_recording(self):
        """Mock hide recording"""
        self.is_recording = False
        print("⚫ Recording overlay hidden")
