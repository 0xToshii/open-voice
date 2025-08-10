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
from src.ui.components.custom_dropdown import CustomDropdown


class SettingsView(QScrollArea):
    """Settings view with provider-based configuration"""

    def __init__(self, settings_manager: ISettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setup_ui()
        self.connect_signals()
        self.update_ui_for_provider()  # Initialize UI state

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

        # Provider section
        provider_section = self.create_provider_section()
        layout.addWidget(provider_section)

        layout.addStretch()

        content_widget.setLayout(layout)
        self.setWidget(content_widget)
        self.setObjectName("settingsView")

    def create_provider_section(self) -> QWidget:
        """Create the provider configuration section"""
        section = QFrame()
        section.setObjectName("settingsSection")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Section title
        section_title = QLabel("Provider Configuration")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        # Provider dropdown
        provider_row = QHBoxLayout()
        provider_label = QLabel("Provider:")
        provider_label.setObjectName("settingLabel")
        provider_label.setMinimumWidth(120)

        self.provider_combo = CustomDropdown()
        self.provider_combo.add_item("Local", "local")
        self.provider_combo.add_item("OpenAI", "openai")

        # Set current provider
        current_provider = self.settings_manager.get_selected_provider()
        if current_provider == "local":
            self.provider_combo.set_current_index(0)
        elif current_provider == "openai":
            self.provider_combo.set_current_index(1)

        provider_row.addWidget(provider_label)
        provider_row.addWidget(self.provider_combo, 1)
        layout.addLayout(provider_row)

        # API Key field (dynamic visibility)
        self.api_key_row = QHBoxLayout()
        self.api_key_label = QLabel("API Key:")
        self.api_key_label.setObjectName("settingLabel")
        self.api_key_label.setMinimumWidth(120)

        self.api_key_input = QLineEdit()
        self.api_key_input.setObjectName("apiKeyInput")
        self.api_key_input.setEnabled(True)
        self.api_key_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.api_key_row.addWidget(self.api_key_label)
        self.api_key_row.addWidget(self.api_key_input, 1)
        layout.addLayout(self.api_key_row)

        # Store widgets for visibility control
        self.api_key_widgets = [self.api_key_label, self.api_key_input]

        section.setLayout(layout)
        return section

    def connect_signals(self):
        """Connect input field changes to settings manager"""
        self.provider_combo.current_index_changed.connect(self.on_provider_changed)
        self.api_key_input.textChanged.connect(self.on_api_key_changed)

        # Listen for external setting changes
        self.settings_manager.setting_changed.connect(self.on_setting_changed)

    def on_provider_changed(self, index: int):
        """Handle provider selection change"""
        selected_provider = self.provider_combo.current_data()
        if selected_provider:
            self.settings_manager.set_selected_provider(selected_provider)
            self.update_ui_for_provider()

    def on_api_key_changed(self, text: str):
        """Handle API key input change"""
        current_provider = self.settings_manager.get_selected_provider()
        if current_provider != "local":  # Only save API key for non-local providers
            self.settings_manager.set_provider_api_key(current_provider, text)

    def update_ui_for_provider(self):
        """Update UI elements based on selected provider"""
        current_provider = self.settings_manager.get_selected_provider()

        if current_provider == "local":
            # Hide API key field for local provider
            for widget in self.api_key_widgets:
                widget.hide()
        else:
            # Show API key field for providers that need it
            for widget in self.api_key_widgets:
                widget.show()

            # Update placeholder and current value based on provider
            if current_provider == "openai":
                self.api_key_input.setPlaceholderText("Enter your OpenAI API key...")
                current_key = self.settings_manager.get_provider_api_key("openai") or ""
                self.api_key_input.setText(current_key)

    def on_setting_changed(self, key: str, value: str):
        """Update UI when settings change externally"""
        if key == "selected_provider":
            # Update provider dropdown
            if value == "local":
                self.provider_combo.set_current_index(0)
            elif value == "openai":
                self.provider_combo.set_current_index(1)
            self.update_ui_for_provider()
        elif key.startswith("provider_api_key_"):
            # Update API key field if it matches current provider
            current_provider = self.settings_manager.get_selected_provider()
            if key == f"provider_api_key_{current_provider}":
                if self.api_key_input.text() != value:
                    self.api_key_input.setText(value)
