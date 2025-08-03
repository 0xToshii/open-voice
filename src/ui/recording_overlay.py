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
        self.setup_animation()
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

        # Set size and position for waveform
        self.setFixedSize(250, 70)  # Larger to accommodate waveform
        self.center_at_bottom()

        # Setup main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(8)

        # Recording text
        self.recording_text = QLabel("Recording...")
        self.recording_text.setObjectName("recordingText")
        self.recording_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Audio waveform widget
        self.waveform = AudioWaveformWidget(bar_count=15)
        self.waveform.setObjectName("audioWaveform")

        # Center the waveform
        waveform_layout = QHBoxLayout()
        waveform_layout.addStretch()
        waveform_layout.addWidget(self.waveform)
        waveform_layout.addStretch()

        main_layout.addWidget(self.recording_text)
        main_layout.addLayout(waveform_layout)

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

    def setup_animation(self):
        """Setup pulsing animation for recording indicator"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_pulse)
        self.animation_timer.setInterval(500)  # Pulse every 500ms
        self.pulse_state = False

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
        self.animation_timer.stop()
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

    def animate_pulse(self):
        """Animate the recording text (no longer needed with waveform)"""
        # Text pulsing effect - alternate opacity
        if self.pulse_state:
            self.recording_text.setStyleSheet("color: rgba(255, 255, 255, 150);")
        else:
            self.recording_text.setStyleSheet("color: rgba(255, 255, 255, 255);")

        self.pulse_state = not self.pulse_state

    def apply_styles(self):
        """Apply CSS styles to the overlay"""
        style = """
        QWidget {
            background-color: rgba(0, 0, 0, 180);
            border-radius: 25px;
            border: 2px solid rgba(255, 255, 255, 100);
        }
        
        #recordingDot {
            font-size: 16px;
        }
        
        #recordingText {
            color: white;
            font-size: 14px;
            font-weight: bold;
        }
        """

        self.setStyleSheet(style)

    def paintEvent(self, event):
        """Custom paint event for better visual effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw semi-transparent background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

        super().paintEvent(event)


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
