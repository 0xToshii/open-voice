from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt
from src.interfaces.settings import ISettingsManager


class SettingsView(QScrollArea):
    """Settings view with API key configuration"""

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
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Title
        title_label = QLabel("SETTINGS")
        title_label.setObjectName("settingsTitle")
        layout.addWidget(title_label)

        # API Keys section
        api_section = self.create_api_keys_section()
        layout.addWidget(api_section)

        layout.addStretch()

        content_widget.setLayout(layout)
        self.setWidget(content_widget)
        self.setObjectName("settingsView")

    def create_api_keys_section(self) -> QWidget:
        """Create the API Keys configuration section"""
        section = QFrame()
        section.setObjectName("settingsSection")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Section title
        section_title = QLabel("API Keys")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        # Cerebras Key
        cerebras_row = QHBoxLayout()
        cerebras_label = QLabel("Cerebras Key:")
        cerebras_label.setObjectName("settingLabel")
        cerebras_label.setMinimumWidth(120)

        self.cerebras_input = QLineEdit()
        self.cerebras_input.setObjectName("apiKeyInput")
        self.cerebras_input.setPlaceholderText("Enter your Cerebras API key...")
        self.cerebras_input.setEnabled(True)
        self.cerebras_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.cerebras_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.cerebras_input.setText(self.settings_manager.get_cerebras_key())

        cerebras_row.addWidget(cerebras_label)
        cerebras_row.addWidget(self.cerebras_input, 1)
        layout.addLayout(cerebras_row)

        # OpenAI Key
        openai_row = QHBoxLayout()
        openai_label = QLabel("OpenAI Key:")
        openai_label.setObjectName("settingLabel")
        openai_label.setMinimumWidth(120)

        self.openai_input = QLineEdit()
        self.openai_input.setObjectName("apiKeyInput")
        self.openai_input.setPlaceholderText("Enter your OpenAI API key...")
        self.openai_input.setEnabled(True)
        self.openai_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.openai_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_input.setText(self.settings_manager.get_openai_key())

        openai_row.addWidget(openai_label)
        openai_row.addWidget(self.openai_input, 1)
        layout.addLayout(openai_row)

        section.setLayout(layout)
        return section

    def connect_signals(self):
        """Connect input field changes to settings manager"""
        self.cerebras_input.textChanged.connect(
            lambda text: self.settings_manager.set_cerebras_key(text)
        )
        self.openai_input.textChanged.connect(
            lambda text: self.settings_manager.set_openai_key(text)
        )

        # Listen for external setting changes
        self.settings_manager.setting_changed.connect(self.on_setting_changed)

    def on_setting_changed(self, key: str, value: str):
        """Update UI when settings change externally"""
        if key == "cerebras_key" and self.cerebras_input.text() != value:
            self.cerebras_input.setText(value)
        elif key == "openai_key" and self.openai_input.text() != value:
            self.openai_input.setText(value)
