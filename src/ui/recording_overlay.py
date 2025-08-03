from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QFont
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

        # Set size and position
        self.setFixedSize(200, 50)
        self.center_at_bottom()

        # Setup layout
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        # Recording indicator
        self.recording_dot = QLabel("🔴")
        self.recording_dot.setObjectName("recordingDot")

        # Recording text
        self.recording_text = QLabel("Recording...")
        self.recording_text.setObjectName("recordingText")

        layout.addWidget(self.recording_dot)
        layout.addWidget(self.recording_text)
        layout.addStretch()

        self.setLayout(layout)

        # Apply styles
        self.apply_styles()

        # Start hidden
        self.hide()

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

    def show_recording(self):
        """Show the recording overlay with animation"""
        if self.is_recording:
            return

        self.is_recording = True
        self.center_at_bottom()  # Ensure proper positioning
        self.show()
        self.raise_()  # Bring to front
        self.animation_timer.start()

    def hide_recording(self):
        """Hide the recording overlay"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.animation_timer.stop()
        self.hide()

    def animate_pulse(self):
        """Animate the pulsing recording indicator"""
        if self.pulse_state:
            self.recording_dot.setText("⚫")  # Dark dot
        else:
            self.recording_dot.setText("🔴")  # Red dot

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
