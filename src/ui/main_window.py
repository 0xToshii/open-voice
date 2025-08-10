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
    QStackedWidget,
    QApplication,
    QDialog,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette
from src.interfaces.data_store import IDataStore, TranscriptEntry
from src.services.recording_service import VoiceRecordingService
from src.ui.recording_overlay import RecordingOverlay
from src.ui.settings_view import SettingsView
from src.ui.custom_instructions_view import CustomInstructionsView
from src.ui.components.delete_confirmation_dialog import DeleteConfirmationDialog
from src.interfaces.settings import ISettingsManager
from src.interfaces.speech_factory import ISpeechEngineRegistry
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

    def __init__(
        self, entry: TranscriptEntry, data_store: IDataStore = None, history_view=None
    ):
        super().__init__()
        self.entry = entry
        self.data_store = data_store
        self.history_view = history_view
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

        # Action buttons - Play, Copy, Delete
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("actionButton")
        self.play_btn.setFixedSize(30, 30)
        self.play_btn.setToolTip("Play recording")
        self.play_btn.clicked.connect(self.on_play_clicked)
        header_layout.addWidget(self.play_btn)

        self.copy_btn = QPushButton("📋")
        self.copy_btn.setObjectName("actionButton")
        self.copy_btn.setFixedSize(30, 30)
        self.copy_btn.setToolTip("Copy text to clipboard")
        self.copy_btn.clicked.connect(self.on_copy_clicked)
        header_layout.addWidget(self.copy_btn)

        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setObjectName("actionButton")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setToolTip("Delete transcript")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        header_layout.addWidget(self.delete_btn)

        layout.addLayout(header_layout)

        # Transcript text bubble - show processed text (what was actually inserted)
        display_text = self.entry.processed_text or self.entry.original_text
        text_bubble = QLabel(display_text)
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

    def on_play_clicked(self):
        """Handle play button click"""
        print(f"Playing audio for transcript {self.entry.id}")
        # TODO: Implement audio playback functionality
        # For now, just show a message
        if self.entry.audio_file_path:
            print(f"Would play audio file: {self.entry.audio_file_path}")
        else:
            print("No audio file available for this transcript")

    def on_copy_clicked(self):
        """Handle copy button click"""
        # Copy processed text (or original if no processed text) to clipboard
        text_to_copy = self.entry.processed_text or self.entry.original_text
        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)
        print(f"Copied to clipboard: '{text_to_copy[:50]}...'")

    def on_delete_clicked(self):
        """Handle delete button click with confirmation dialog"""
        if not self.data_store:
            print("No data store available for deletion")
            return

        # Show confirmation dialog
        dialog = DeleteConfirmationDialog(self)
        result = dialog.exec()

        if result == QDialog.Accepted:
            # User confirmed deletion
            try:
                success = self.data_store.delete_transcript(self.entry.id)
                if success:
                    print(f"Successfully deleted transcript {self.entry.id}")
                    # Notify parent BEFORE deleting self
                    if self.history_view:
                        self.history_view.on_transcript_deleted(self.entry.id)
                    # Efficient deletion - just remove this widget
                    self.hide()
                    self.deleteLater()
                else:
                    print(f"Failed to delete transcript {self.entry.id}")
            except Exception as e:
                print(f"Error deleting transcript {self.entry.id}: {e}")
        else:
            # User cancelled
            print(f"Deletion cancelled for transcript {self.entry.id}")


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
        self.content_widget.setObjectName("historyContent")
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        self.content_widget.setLayout(self.content_layout)
        self.setWidget(self.content_widget)

        self.setObjectName("historyView")

    def load_transcripts(self):
        """Load and display transcript entries"""
        try:
            transcripts = self.data_store.get_transcripts(limit=50)

            if len(transcripts) == 0:
                # Show empty state if no transcripts
                self.add_empty_state_widget()
            else:
                # Add transcript bubbles
                for transcript in transcripts:
                    bubble = TranscriptBubble(transcript, self.data_store, self)
                    self.content_layout.addWidget(bubble)

            self.content_layout.addStretch()

        except Exception as e:
            print(f"Error loading transcripts: {e}")
            # Show error state or empty state as fallback
            self.add_empty_state_widget()
            self.content_layout.addStretch()

    def add_new_transcript(self, entry: TranscriptEntry):
        """Add a new transcript bubble at the top"""
        # Remove empty state widget if it exists (since we're adding a transcript)
        self.remove_empty_state_widget()

        bubble = TranscriptBubble(entry, self.data_store, self)
        self.content_layout.insertWidget(0, bubble)

    def on_transcript_deleted(self, transcript_id: int):
        """Handle efficient transcript deletion and manage empty state"""
        print(f"Transcript {transcript_id} deleted from view")

        # Check database (source of truth) for remaining transcripts
        try:
            remaining_transcripts = self.data_store.get_transcripts(limit=1)
            remaining_count = len(remaining_transcripts)
            print(f"Remaining transcripts: {remaining_count}")

            if remaining_count == 0:
                self.add_empty_state_widget()
        except Exception as e:
            print(f"Error checking remaining transcripts: {e}")

    def remove_empty_state_widget(self):
        """Remove empty state widget if it exists"""
        for i in range(self.content_layout.count()):
            widget = self.content_layout.itemAt(i).widget()
            if widget and widget.objectName() == "emptyStateWidget":
                self.content_layout.removeWidget(widget)
                widget.deleteLater()
                break

    def add_empty_state_widget(self):
        """Add empty state message when no transcripts exist"""
        empty_widget = QWidget()
        empty_widget.setObjectName("emptyStateWidget")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        # Empty state message
        title_label = QLabel("No transcripts yet")
        title_label.setObjectName("emptyStateTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel("Start recording to see your transcripts appear here")
        desc_label.setObjectName("emptyStateDesc")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        empty_widget.setLayout(layout)

        # Insert before the stretch (which should be the last item)
        stretch_index = self.content_layout.count() - 1
        if stretch_index >= 0:
            self.content_layout.insertWidget(stretch_index, empty_widget)
        else:
            self.content_layout.addWidget(empty_widget)

        print("Added empty state widget")

    def refresh_transcripts(self):
        """Refresh the transcript list"""
        # Clear existing widgets
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Reload transcripts
        self.load_transcripts()


class PlaceholderView(QScrollArea):
    """Placeholder view for unimplemented pages"""

    def __init__(self, title: str):
        super().__init__()
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        content_widget = QWidget()
        content_widget.setObjectName("placeholderContent")
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("placeholderTitle")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(f"Coming soon.")
        desc_label.setObjectName("placeholderDesc")
        layout.addWidget(desc_label)

        layout.addStretch()
        content_widget.setLayout(layout)
        self.setWidget(content_widget)

        self.setObjectName("placeholderView")


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(
        self,
        data_store: IDataStore,
        settings_manager: ISettingsManager,
        recording_service: VoiceRecordingService = None,
    ):
        super().__init__()
        self.data_store = data_store
        self.settings_manager = settings_manager
        self.recording_service = recording_service
        self.current_view = "Settings"

        # Create recording overlay on main thread
        self.recording_overlay = RecordingOverlay()

        self.setup_ui()
        self.apply_styles()

        # Connect recording service if provided
        if self.recording_service:
            self.connect_recording_service()

        # Connect settings changes to speech engine switching
        self.connect_settings_changes()

    def connect_recording_service(self):
        """Connect signals from the recording service"""
        if self.recording_service:
            self.recording_service.transcript_created.connect(
                self.on_transcript_created
            )
            self.recording_service.recording_started.connect(self.on_recording_started)
            self.recording_service.recording_stopped.connect(self.on_recording_stopped)

            # Connect audio recorder to recording overlay for real-time waveform
            try:
                audio_recorder = self.recording_service.get_audio_recorder()
                if audio_recorder:
                    self.recording_overlay.set_audio_recorder(audio_recorder)
                    print("🔗 Connected audio recorder to recording overlay")
            except Exception as e:
                print(f"⚠️ Could not connect audio recorder to overlay: {e}")

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

        # Allow window to accept focus for input fields
        # Note: Removed WindowDoesNotAcceptFocus to enable text input

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

        # Content area - create QStackedWidget for view switching
        self.content_stack = QStackedWidget()

        # Create all views and add them to the stack
        self.history_view = HistoryView(self.data_store)
        self.settings_view = SettingsView(self.settings_manager)
        self.dictionary_view = PlaceholderView("Dictionary")
        self.instructions_view = CustomInstructionsView(self.settings_manager)

        # Add views to stack
        self.content_stack.addWidget(self.history_view)
        self.content_stack.addWidget(self.settings_view)
        self.content_stack.addWidget(self.dictionary_view)
        self.content_stack.addWidget(self.instructions_view)

        # Show settings view by default
        self.content_stack.setCurrentWidget(self.settings_view)
        main_layout.addWidget(self.content_stack, 1)

        central_widget.setLayout(main_layout)

    def on_menu_item_clicked(self, item_name: str):
        """Handle sidebar menu item clicks using QStackedWidget"""
        self.current_view = item_name

        # Switch to the appropriate view using QStackedWidget
        if item_name == "History":
            self.content_stack.setCurrentWidget(self.history_view)
            # No refresh needed - history view is always up to date
        elif item_name == "Settings":
            self.content_stack.setCurrentWidget(self.settings_view)
        elif item_name == "Dictionary":
            self.content_stack.setCurrentWidget(self.dictionary_view)
        elif item_name == "Instructions":
            self.content_stack.setCurrentWidget(self.instructions_view)
        else:
            print(f"Unknown menu item: {item_name}")
            return

        print(f"📋 Switched to {item_name} view")

    def add_transcript_entry(self, entry: TranscriptEntry):
        """Add a new transcript entry to the history"""
        # Always add to history view regardless of current tab
        self.history_view.add_new_transcript(entry)

    def connect_settings_changes(self):
        """Connect to settings changes to switch speech engines dynamically"""
        self.settings_manager.setting_changed.connect(self.on_setting_changed)

    def on_setting_changed(self, setting_name: str, value: str):
        """Handle settings changes - switch speech engine when OpenAI key changes"""
        if setting_name == "openai_key" and self.recording_service:
            try:
                # TODO: Access to registry should come from DI container
                # For now, we'll let the recording service handle engine switching
                # by calling its internal methods that use the proper DI approach

                # Log the potential engine switch
                print(f"🔄 Settings changed: {setting_name} = {value}")
                print("   Engine switching will be handled by the recording service")

            except Exception as e:
                print(f"❌ Failed to handle settings change: {e}")

    def apply_styles(self):
        """Apply CSS styles to the window"""
        style = """
        /* Force light theme everywhere */
        QMainWindow {
            background-color: #ffffff !important;
        }
        
        QScrollArea {
            background-color: #f5f5f5 !important;
        }
        
        #sidebar {
            background-color: #ffffff !important;
            border-right: 1px solid #e8e8e8;
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
            background-color: transparent;
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
            background-color: #f5f5f5 !important;
            border: none;
        }
        
        #historyContent {
            background-color: #f5f5f5 !important;
        }
        
        #transcriptEntry {
            margin-bottom: 10px;
            background-color: transparent;
        }
        
        #transcriptHeader {
            color: #666;
            font-size: 12px;
            margin-bottom: 5px;
            background-color: transparent;
        }
        
        #historyView #transcriptBubble {
            background-color: #4a4a4a !important;
            color: white !important;
            padding: 15px 20px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.4;
        }
        
        #actionButton {
            border: 1px solid #ddd;
            background-color: #f8f8f8;
            color: #333;
            font-size: 14px;
            padding: 5px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        #actionButton:hover {
            background-color: #e8e8e8;
            border-color: #ccc;
            color: #000;
        }
        
        #actionButton:pressed {
            background-color: #ddd;
            border-color: #bbb;
        }
        
        /* Empty State Styles */
        #emptyStateWidget {
            background-color: transparent;
            padding: 40px;
        }
        
        #emptyStateTitle {
            font-size: 18px;
            font-weight: 600;
            color: #666;
            background-color: transparent;
        }
        
        #emptyStateDesc {
            font-size: 14px;
            color: #999;
            background-color: transparent;
        }
        
        /* Settings View Styles */
        #settingsView {
            background-color: #f5f5f5 !important;
            border: none;
        }
        
        #settingsView QWidget {
            background-color: #f5f5f5 !important;
        }
        
        #settingsTitle {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            background-color: transparent;
        }
        
        #settingsSection {
            background-color: #ffffff !important;
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        #sectionTitle {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            background-color: transparent;
        }
        
        #settingLabel {
            font-size: 14px;
            font-weight: 500;
            color: #555;
            padding: 5px 0;
            background-color: transparent;
        }
        
        #apiKeyInput {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: #ffffff !important;
            color: #333333;
        }
        
        #apiKeyInput:focus {
            border-color: #007AFF;
            outline: none;
        }
        
        #apiKeyInput::placeholder {
            color: #999;
        }
        
        /* Custom Instructions View Styles */
        #customInstructionsView {
            background-color: #f5f5f5 !important;
            border: none;
        }
        
        #customInstructionsView QWidget {
            background-color: #f5f5f5 !important;
        }
        
        #customInstructionsTitle {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            background-color: transparent;
        }
        
        #customInstructionsDescription {
            font-size: 14px;
            color: #666;
            margin-bottom: 20px;
            background-color: transparent;
            line-height: 1.4;
        }
        
        #instructionsSection {
            background-color: #ffffff !important;
            border: 1px solid #e8e8e8;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        #customInstructionsInput {
            border: 1px solid #d0d0d0;
            border-radius: 6px;
            padding: 12px;
            font-size: 14px;
            background-color: #ffffff !important;
            color: #333333;
            line-height: 1.4;
        }
        
        #customInstructionsInput:focus {
            border-color: #007AFF;
            outline: none;
        }
        
        #customInstructionsInput::placeholder {
            color: #999;
        }
        
        /* Placeholder View Styles */
        #placeholderView {
            background-color: #f5f5f5 !important;
            border: none;
        }
        
        #placeholderContent {
            background-color: #f5f5f5 !important;
        }
        
        #placeholderTitle {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            background-color: transparent;
        }
        
        #placeholderDesc {
            font-size: 16px;
            color: #666;
            background-color: transparent;
        }
        """

        self.setStyleSheet(style)
        print("🎨 Applied light theme CSS styles")
