from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt
from src.interfaces.settings import ISettingsManager


class CustomInstructionsView(QScrollArea):
    """Custom Instructions view for style preferences and text processing instructions"""

    def __init__(self, settings_manager: ISettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Title
        title_label = QLabel("Custom Instructions")
        title_label.setObjectName("customInstructionsTitle")
        layout.addWidget(title_label)

        # Description - tighter spacing with title
        description_label = QLabel(
            'Provide style preferences or instructions. For example: "Use all lowercase words," or "Use bullet points when creating lists."'
        )
        description_label.setObjectName("customInstructionsDescription")
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        # Instructions input section - closer to description
        instructions_section = self.create_instructions_section()
        layout.addWidget(instructions_section)

        layout.addStretch()

        content_widget.setLayout(layout)
        self.setWidget(content_widget)
        self.setObjectName("customInstructionsView")

    def create_instructions_section(self) -> QWidget:
        """Create the instructions input section"""
        section = QFrame()
        section.setObjectName("instructionsSection")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(8)

        # Text area for instructions
        self.instructions_input = QTextEdit()
        self.instructions_input.setObjectName("customInstructionsInput")
        self.instructions_input.setPlaceholderText(
            "Use all lowercase words, other than proper nouns. Use dashes instead of commas when it makes sense to."
        )
        self.instructions_input.setMinimumHeight(150)
        self.instructions_input.setMaximumHeight(300)

        # Load existing instructions
        existing_instructions = self.settings_manager.get_custom_instructions()
        if existing_instructions:
            self.instructions_input.setPlainText(existing_instructions)

        layout.addWidget(self.instructions_input)

        section.setLayout(layout)
        return section

    def connect_signals(self):
        """Connect input field changes to settings manager"""
        self.instructions_input.textChanged.connect(self.on_instructions_changed)

        # Listen for external setting changes
        self.settings_manager.setting_changed.connect(self.on_setting_changed)

    def on_instructions_changed(self):
        """Handle text changes in the instructions field"""
        text = self.instructions_input.toPlainText()
        self.settings_manager.set_custom_instructions(text)

    def on_setting_changed(self, key: str, value: str):
        """Update UI when settings change externally"""
        if (
            key == "custom_instructions"
            and self.instructions_input.toPlainText() != value
        ):
            self.instructions_input.setPlainText(value)
