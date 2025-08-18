from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QWidget,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from src.ui.audio_waveform import AudioWaveformWidget
from src.services.audio_recorder import PyAudioRecorder
from typing import Optional
import threading


class MicrophoneTestDialog(QDialog):
    """Modal dialog for testing microphone with real-time audio level visualization"""

    def __init__(self, device_id: str, device_name: str, parent=None):
        super().__init__(parent)
        self.device_id = device_id
        self.device_name = device_name
        self.recorder: Optional[PyAudioRecorder] = None
        self.is_testing = False

        # Timer for updating audio levels
        self.level_update_timer = QTimer()
        self.level_update_timer.timeout.connect(self.update_audio_level)
        self.level_update_timer.setInterval(33)  # ~30fps for smooth visualization

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Test Microphone")
        self.setModal(True)
        self.setFixedSize(500, 280)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header section
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel("Test Microphone")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        subtitle_label = QLabel("Speak to test your selected microphone")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #666666;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Device info section
        device_frame = QFrame()
        device_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 16px;
            }
        """
        )

        device_layout = QVBoxLayout()
        device_layout.setContentsMargins(16, 16, 16, 16)

        # Device name and status row
        device_info_layout = QHBoxLayout()

        self.device_name_label = QLabel(self.device_name)
        device_name_font = QFont()
        device_name_font.setPointSize(14)
        device_name_font.setBold(True)
        self.device_name_label.setFont(device_name_font)

        self.status_label = QLabel("Inactive")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_font = QFont()
        status_font.setPointSize(12)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #6c757d;")

        device_info_layout.addWidget(self.device_name_label)
        device_info_layout.addWidget(self.status_label)
        device_layout.addLayout(device_info_layout)

        # Audio level visualization
        level_layout = QHBoxLayout()
        level_layout.setContentsMargins(0, 16, 0, 0)

        # Microphone icon (simple text for now)
        mic_label = QLabel("🎤")
        mic_font = QFont()
        mic_font.setPointSize(16)
        mic_label.setFont(mic_font)

        # Audio waveform widget (configured as horizontal bar)
        self.audio_waveform = AudioWaveformWidget(bar_count=20, parent=self)

        # Speaker icon (simple text for now)
        speaker_label = QLabel("🔊")
        speaker_font = QFont()
        speaker_font.setPointSize(16)
        speaker_label.setFont(speaker_font)

        level_layout.addWidget(mic_label)
        level_layout.addWidget(self.audio_waveform, 1)
        level_layout.addWidget(speaker_label)
        device_layout.addLayout(level_layout)

        device_frame.setLayout(device_layout)
        layout.addWidget(device_frame)

        # Instructions text
        self.instructions_label = QLabel("You should hear your voice")
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions_font = QFont()
        instructions_font.setPointSize(12)
        self.instructions_label.setFont(instructions_font)
        self.instructions_label.setStyleSheet("color: #666666;")
        self.instructions_label.hide()  # Hidden initially

        layout.addWidget(self.instructions_label)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # Start/Stop button
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.setFixedSize(120, 40)
        self.start_stop_button.setStyleSheet(
            """
            QPushButton {
                background-color: #212529;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #343a40;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """
        )

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.setFixedSize(120, 40)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                background-color: #f8f9fa;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """
        )

        button_layout.addStretch()
        button_layout.addWidget(self.start_stop_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def setup_connections(self):
        """Setup signal connections"""
        self.start_stop_button.clicked.connect(self.toggle_testing)
        self.close_button.clicked.connect(self.close_dialog)

    def toggle_testing(self):
        """Toggle microphone testing on/off"""
        if not self.is_testing:
            self.start_testing()
        else:
            self.stop_testing()

    def start_testing(self):
        """Start microphone testing"""
        try:
            # Create recorder with selected device
            self.recorder = PyAudioRecorder(device_id=self.device_id)

            # Start recording
            self.recorder.start_recording()

            # Update UI state
            self.is_testing = True
            self.start_stop_button.setText("Stop")
            self.start_stop_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """
            )
            self.status_label.setText("Active")
            self.status_label.setStyleSheet("color: #28a745;")
            self.instructions_label.show()

            # Start audio level updates
            self.audio_waveform.start_animation()
            self.level_update_timer.start()

            print(f"Started microphone test for device: {self.device_name}")

        except Exception as e:
            print(f"Failed to start microphone test: {e}")
            self.show_error(
                "Failed to access microphone. Please check device permissions and try again."
            )

    def stop_testing(self):
        """Stop microphone testing"""
        try:
            # Stop audio level updates
            self.level_update_timer.stop()
            self.audio_waveform.stop_animation()

            # Stop recording
            if self.recorder:
                self.recorder.stop_recording()
                self.recorder = None

            # Update UI state
            self.is_testing = False
            self.start_stop_button.setText("Start")
            self.start_stop_button.setStyleSheet(
                """
                QPushButton {
                    background-color: #212529;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #343a40;
                }
                QPushButton:pressed {
                    background-color: #495057;
                }
            """
            )
            self.status_label.setText("Inactive")
            self.status_label.setStyleSheet("color: #6c757d;")
            self.instructions_label.hide()

            print("Stopped microphone test")

        except Exception as e:
            print(f"Error stopping microphone test: {e}")

    def update_audio_level(self):
        """Update audio level visualization"""
        if self.recorder and self.is_testing:
            try:
                # Get current audio level from recorder
                level = self.recorder.get_audio_level()

                # Update waveform widget
                self.audio_waveform.update_audio_level(level)

            except Exception as e:
                print(f"Error updating audio level: {e}")

    def show_error(self, message: str):
        """Show error message to user"""
        self.status_label.setText("Error")
        self.status_label.setStyleSheet("color: #dc3545;")
        self.instructions_label.setText(message)
        self.instructions_label.setStyleSheet("color: #dc3545;")
        self.instructions_label.show()

    def close_dialog(self):
        """Close the dialog"""
        # Ensure testing is stopped
        if self.is_testing:
            self.stop_testing()
        self.accept()

    def closeEvent(self, event):
        """Handle dialog close event"""
        # Ensure testing is stopped when dialog is closed
        if self.is_testing:
            self.stop_testing()
        super().closeEvent(event)
