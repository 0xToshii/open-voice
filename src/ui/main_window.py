from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette
from src.interfaces.data_store import IDataStore, TranscriptEntry
from src.services.recording_service import VoiceRecordingService
from src.ui.recording_overlay import RecordingOverlay
from typing import List
from datetime import datetime


class SidebarWidget(QWidget):
    """Sidebar navigation widget"""

    # Signal emitted when a menu item is clicked
    menu_item_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.active_item = "History"

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)

        # App title
        title_label = QLabel("OPEN VOICE")
        title_label.setObjectName("appTitle")
        layout.addWidget(title_label)

        layout.addSpacing(30)

        # Menu items
        menu_items = [
            ("⚙️", "Settings"),
            ("📖", "Dictionary"),
            ("📄", "Instructions"),
            ("🕐", "History"),
        ]

        for icon, text in menu_items:
            self.add_menu_item(layout, icon, text)

        layout.addStretch()

        self.setLayout(layout)
        self.setObjectName("sidebar")

    def add_menu_item(self, layout: QVBoxLayout, icon: str, text: str):
        container = QWidget()
        container.setObjectName("menuItem")

        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(15, 10, 15, 10)

        icon_label = QLabel(icon)
        text_label = QLabel(text)

        item_layout.addWidget(icon_label)
        item_layout.addWidget(text_label)
        item_layout.addStretch()

        container.setLayout(item_layout)
        container.mousePressEvent = lambda event, name=text: self.on_menu_item_clicked(
            name
        )

        layout.addWidget(container)

    def on_menu_item_clicked(self, item_name: str):
        self.active_item = item_name
        self.menu_item_clicked.emit(item_name)
        self.update_active_styling()

    def update_active_styling(self):
        # Update styling to show active item
        # This would be implemented with proper CSS styling
        pass


class TranscriptBubble(QWidget):
    """Individual transcript bubble widget"""

    def __init__(self, entry: TranscriptEntry):
        super().__init__()
        self.entry = entry
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with timestamp and duration
        header_layout = QHBoxLayout()

        time_ago = self.format_time_ago(self.entry.timestamp)
        duration_str = self.format_duration(self.entry.duration)

        header_label = QLabel(f"{time_ago} • {duration_str}")
        header_label.setObjectName("transcriptHeader")

        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Action buttons
        action_buttons = ["▶️", "🔄", "👍", "👎", "📋", "⋯"]
        for btn_text in action_buttons:
            btn = QPushButton(btn_text)
            btn.setObjectName("actionButton")
            btn.setFixedSize(30, 30)
            header_layout.addWidget(btn)

        layout.addLayout(header_layout)

        # Transcript text bubble
        text_bubble = QLabel(self.entry.original_text)
        text_bubble.setObjectName("transcriptBubble")
        text_bubble.setWordWrap(True)
        text_bubble.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        layout.addWidget(text_bubble)

        self.setLayout(layout)
        self.setObjectName("transcriptEntry")

    def format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as 'X minutes ago'"""
        now = datetime.now()
        diff = now - timestamp

        if diff.total_seconds() < 60:
            return "Just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"

    def format_duration(self, duration: float) -> str:
        """Format duration as MM:SS"""
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes:02d}:{seconds:02d}"


class HistoryView(QScrollArea):
    """Main history view showing transcript bubbles"""

    def __init__(self, data_store: IDataStore):
        super().__init__()
        self.data_store = data_store
        self.setup_ui()
        self.load_transcripts()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        self.content_widget.setLayout(self.content_layout)
        self.setWidget(self.content_widget)

        self.setObjectName("historyView")

    def load_transcripts(self):
        """Load and display transcript entries"""
        transcripts = self.data_store.get_transcripts(limit=50)

        for transcript in transcripts:
            bubble = TranscriptBubble(transcript)
            self.content_layout.addWidget(bubble)

        self.content_layout.addStretch()

    def add_new_transcript(self, entry: TranscriptEntry):
        """Add a new transcript bubble at the top"""
        bubble = TranscriptBubble(entry)
        self.content_layout.insertWidget(0, bubble)

    def refresh_transcripts(self):
        """Refresh the transcript list"""
        # Clear existing widgets
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Reload transcripts
        self.load_transcripts()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(
        self, data_store: IDataStore, recording_service: VoiceRecordingService = None
    ):
        super().__init__()
        self.data_store = data_store
        self.recording_service = recording_service
        self.current_view = "History"

        # Create recording overlay on main thread
        self.recording_overlay = RecordingOverlay()

        self.setup_ui()
        self.apply_styles()

        # Connect recording service if provided
        if self.recording_service:
            self.connect_recording_service()

    def connect_recording_service(self):
        """Connect signals from the recording service"""
        if self.recording_service:
            self.recording_service.transcript_created.connect(
                self.on_transcript_created
            )
            self.recording_service.recording_started.connect(self.on_recording_started)
            self.recording_service.recording_stopped.connect(self.on_recording_stopped)

    def on_transcript_created(self, entry: TranscriptEntry):
        """Handle new transcript creation from recording service"""
        # Add to data store is already handled by the service
        # Just update the UI
        self.add_transcript_entry(entry)

    def on_recording_started(self):
        """Handle recording started signal (thread-safe)"""
        print("📱 UI: Showing recording overlay")
        self.recording_overlay.show_recording()

    def on_recording_stopped(self):
        """Handle recording stopped signal (thread-safe)"""
        print("📱 UI: Hiding recording overlay")
        self.recording_overlay.hide_recording()

    def setup_ui(self):
        self.setWindowTitle("Open Voice")
        self.setMinimumSize(800, 600)

        # Configure window to never steal focus
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowDoesNotAcceptFocus)

        # Ensure window doesn't activate automatically
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.menu_item_clicked.connect(self.on_menu_item_clicked)
        main_layout.addWidget(self.sidebar)

        # Content area
        self.history_view = HistoryView(self.data_store)
        main_layout.addWidget(self.history_view, 1)

        central_widget.setLayout(main_layout)

    def on_menu_item_clicked(self, item_name: str):
        """Handle sidebar menu item clicks"""
        self.current_view = item_name

        if item_name == "History":
            # Already showing history view
            self.history_view.refresh_transcripts()
        else:
            # Placeholder for other views
            print(f"Clicked on {item_name} - not implemented yet")

    def add_transcript_entry(self, entry: TranscriptEntry):
        """Add a new transcript entry to the history"""
        if self.current_view == "History":
            self.history_view.add_new_transcript(entry)

    def apply_styles(self):
        """Apply CSS styles to the window"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        #sidebar {
            background-color: #ffffff;
            border-right: 1px solid #e0e0e0;
            min-width: 200px;
            max-width: 200px;
        }
        
        #appTitle {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            padding: 0 15px;
        }
        
        #menuItem {
            padding: 5px;
            border-radius: 8px;
            margin: 2px 10px;
            color: #333333;
        }
        
        #menuItem:hover {
            background-color: #f0f0f0;
        }
        
        #menuItem QLabel {
            color: #333333;
            font-weight: 500;
        }
        
        #upgradeButton {
            background-color: #007AFF;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px;
            margin: 10px;
            font-weight: bold;
        }
        
        #historyView {
            background-color: #f8f9fa;
            border: none;
        }
        
        #transcriptEntry {
            margin-bottom: 10px;
        }
        
        #transcriptHeader {
            color: #666;
            font-size: 12px;
            margin-bottom: 5px;
        }
        
        #transcriptBubble {
            background-color: #333;
            color: white;
            padding: 15px 20px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        #actionButton {
            border: none;
            background: transparent;
            font-size: 14px;
            padding: 5px;
            border-radius: 4px;
        }
        
        #actionButton:hover {
            background-color: #e0e0e0;
        }
        """

        self.setStyleSheet(style)
