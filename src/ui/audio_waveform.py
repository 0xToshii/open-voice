from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen
from typing import List, Optional
import math


class AudioWaveformWidget(QWidget):
    """Real-time audio waveform visualization widget"""

    def __init__(self, bar_count: int = 12, parent=None):
        super().__init__(parent)

        # Configuration
        self.bar_count = bar_count
        self.bar_width = 4
        self.bar_spacing = 2
        self.max_bar_height = 30
        self.min_bar_height = 3

        # Audio level history (rolling buffer)
        self.audio_levels: List[float] = [0.0] * bar_count
        self.current_level = 0.0

        # Animation properties
        self.smooth_levels: List[float] = [0.0] * bar_count
        self.target_levels: List[float] = [0.0] * bar_count

        # Timer for smooth animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(16)  # ~60fps

        # Setup widget
        self.setup_widget()

    def setup_widget(self):
        """Setup widget properties"""
        # Calculate widget size based on bars
        total_width = (self.bar_width * self.bar_count) + (
            self.bar_spacing * (self.bar_count - 1)
        )
        self.setFixedSize(total_width, self.max_bar_height + 4)  # +4 for padding

        # Transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def start_animation(self):
        """Start the waveform animation"""
        self.animation_timer.start()

    def stop_animation(self):
        """Stop the waveform animation"""
        self.animation_timer.stop()
        # Fade out animation
        self.fade_to_silence()

    def update_audio_level(self, level: float):
        """Update current audio level (0.0 to 1.0)"""
        # Clamp level to valid range
        self.current_level = max(0.0, min(1.0, level))

        # Add some randomness for more dynamic visualization
        # (Real audio has natural variations, this makes it look more alive)
        if self.current_level > 0.1:
            import random

            variation = random.uniform(0.8, 1.2)
            self.current_level = min(1.0, self.current_level * variation)

    def update_animation(self):
        """Update animation frame (called ~60fps)"""
        # Shift audio levels (new level goes to the rightmost bar)
        self.audio_levels = self.audio_levels[1:] + [self.current_level]

        # Create target levels with some variation for visual interest
        for i, level in enumerate(self.audio_levels):
            # Add some neighbor influence for smoother wave effect
            neighbor_influence = 0.0
            if i > 0:
                neighbor_influence += self.audio_levels[i - 1] * 0.3
            if i < len(self.audio_levels) - 1:
                neighbor_influence += self.audio_levels[i + 1] * 0.3

            # Combine actual level with neighbor influence
            influenced_level = (level * 0.4) + (neighbor_influence * 0.6)
            self.target_levels[i] = influenced_level

        # Smooth interpolation to target levels
        for i in range(len(self.smooth_levels)):
            # Lerp (linear interpolation) for smooth animation
            diff = self.target_levels[i] - self.smooth_levels[i]
            self.smooth_levels[i] += (
                diff * 0.3
            )  # Adjust speed (0.1 = slower, 0.5 = faster)

        # Trigger repaint
        self.update()

    def fade_to_silence(self):
        """Gradually fade all bars to silence"""
        for i in range(len(self.audio_levels)):
            self.audio_levels[i] *= 0.7  # Fade factor
            self.target_levels[i] *= 0.7
        self.current_level *= 0.7

    def paintEvent(self, event):
        """Custom paint event to draw the waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))  # Transparent

        # Draw each bar
        for i, level in enumerate(self.smooth_levels):
            self.draw_bar(painter, i, level)

    def draw_bar(self, painter: QPainter, index: int, level: float):
        """Draw a single waveform bar"""
        # Calculate bar position
        x = index * (self.bar_width + self.bar_spacing)

        # Calculate bar height based on level
        bar_height = self.min_bar_height + (
            level * (self.max_bar_height - self.min_bar_height)
        )

        # Center the bar vertically
        y = (self.height() - bar_height) // 2

        # Create bar rectangle
        bar_rect = QRect(int(x), int(y), self.bar_width, int(bar_height))

        # Choose color based on audio level
        color = self.get_level_color(level)

        # Draw bar with rounded corners effect
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar_rect, 2, 2)

        # Add subtle glow effect for higher levels
        if level > 0.5:
            self.draw_glow_effect(painter, bar_rect, color, level)

    def draw_glow_effect(
        self, painter: QPainter, rect: QRect, color: QColor, intensity: float
    ):
        """Draw a subtle glow effect around the bar"""
        # Create glow color (same as bar but more transparent)
        glow_color = QColor(color)
        glow_color.setAlphaF(0.3 * intensity)

        # Draw slightly larger rectangle for glow
        glow_rect = QRect(
            rect.x() - 1, rect.y() - 1, rect.width() + 2, rect.height() + 2
        )

        painter.setBrush(glow_color)
        painter.drawRoundedRect(glow_rect, 3, 3)

    def get_level_color(self, level: float) -> QColor:
        """Get color for audio level (quiet → loud = blue → green → yellow → red)"""
        if level < 0.1:
            # Very quiet - dark blue
            return QColor(50, 100, 200, 100)
        elif level < 0.3:
            # Quiet - blue to cyan
            t = (level - 0.1) / 0.2
            return QColor(
                int(50 + t * 50),  # R: 50 → 100
                int(100 + t * 100),  # G: 100 → 200
                int(200),  # B: 200
                int(100 + t * 100),  # A: 100 → 200
            )
        elif level < 0.6:
            # Medium - cyan to green
            t = (level - 0.3) / 0.3
            return QColor(
                int(100 - t * 50),  # R: 100 → 50
                int(200),  # G: 200
                int(200 - t * 100),  # B: 200 → 100
                200,
            )
        elif level < 0.8:
            # Loud - green to yellow
            t = (level - 0.6) / 0.2
            return QColor(
                int(50 + t * 150),  # R: 50 → 200
                int(200),  # G: 200
                int(100 - t * 100),  # B: 100 → 0
                220,
            )
        else:
            # Very loud - yellow to red
            t = (level - 0.8) / 0.2
            return QColor(
                int(200 + t * 55),  # R: 200 → 255
                int(200 - t * 200),  # G: 200 → 0
                0,  # B: 0
                240,
            )

    def get_widget_size(self) -> tuple:
        """Get the recommended widget size"""
        total_width = (self.bar_width * self.bar_count) + (
            self.bar_spacing * (self.bar_count - 1)
        )
        return (total_width, self.max_bar_height + 4)
