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
from PySide6.QtWidgets import QPushButton
from src.interfaces.settings import ISettingsManager
from src.ui.components.custom_dropdown import CustomDropdown
from src.services.audio_device_manager import AudioDeviceManager


class SettingsView(QScrollArea):
    """Settings view with provider-based configuration"""

    def __init__(self, settings_manager: ISettingsManager):
        super().__init__()
        self.settings_manager = settings_manager
        self.audio_device_manager = AudioDeviceManager()
        self.setup_ui()
        self.connect_signals()
        self.update_ui_for_provider()  # Initialize UI state
        self.update_microphone_dropdown()  # Initialize microphone devices

    def setup_ui(self):
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title_label = QLabel("Settings")
        title_label.setObjectName("settingsTitle")
        layout.addWidget(title_label)

        # Provider section
        provider_section = self.create_provider_section()
        layout.addWidget(provider_section)

        # Microphone section
        microphone_section = self.create_microphone_section()
        layout.addWidget(microphone_section)

        layout.addStretch()

        content_widget.setLayout(layout)
        self.setWidget(content_widget)
        self.setObjectName("settingsView")

    def create_provider_section(self) -> QWidget:
        """Create the provider configuration section"""
        section = QFrame()
        section.setObjectName("settingsSection")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(15)

        # Section title
        section_title = QLabel("API Provider")
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
        self.provider_combo.add_item("Groq", "groq")

        # Set current provider
        current_provider = self.settings_manager.get_selected_provider()
        if current_provider == "local":
            self.provider_combo.set_current_index(0)
        elif current_provider == "openai":
            self.provider_combo.set_current_index(1)
        elif current_provider == "groq":
            self.provider_combo.set_current_index(2)

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
        self.microphone_combo.current_index_changed.connect(self.on_microphone_changed)

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

        # Always show API key widgets
        for widget in self.api_key_widgets:
            widget.show()

        if current_provider == "local":
            # For local provider: disable input and show "Not required"
            self.api_key_input.setEnabled(False)
            self.api_key_input.setPlaceholderText("Not required")
            self.api_key_input.clear()
        else:
            # For other providers: enable input and set appropriate placeholder
            self.api_key_input.setEnabled(True)

            if current_provider == "openai":
                self.api_key_input.setPlaceholderText("Enter your OpenAI API key")
                current_key = self.settings_manager.get_provider_api_key("openai") or ""
                self.api_key_input.setText(current_key)
            elif current_provider == "groq":
                self.api_key_input.setPlaceholderText("Enter your Groq API key")
                current_key = self.settings_manager.get_provider_api_key("groq") or ""
                self.api_key_input.setText(current_key)

    def create_microphone_section(self) -> QWidget:
        """Create the microphone configuration section"""
        section = QFrame()
        section.setObjectName("settingsSection")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(15)

        # Section title
        section_title = QLabel("Microphone")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)

        # Microphone dropdown row
        microphone_row = QHBoxLayout()
        microphone_label = QLabel("Device:")
        microphone_label.setObjectName("settingLabel")
        microphone_label.setMinimumWidth(120)

        self.microphone_combo = CustomDropdown()

        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.clicked.connect(self.on_refresh_devices)
        self.refresh_button.setToolTip("Refresh device list")

        # Style the refresh button to look like Aqua Voice - flat and borderless
        self.refresh_button.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666666;
                font-size: 16px;
                font-weight: normal;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #333333;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
                color: #000000;
            }
        """
        )

        microphone_row.addWidget(microphone_label)
        microphone_row.addWidget(self.microphone_combo, 1)
        microphone_row.addWidget(self.refresh_button)
        layout.addLayout(microphone_row)

        section.setLayout(layout)
        return section

    def update_microphone_dropdown(self):
        """Update microphone dropdown with available devices"""
        try:
            # Clear existing items
            self.microphone_combo.clear()

            # Get available devices
            devices = self.audio_device_manager.get_input_devices()

            # Add devices to dropdown
            for device in devices:
                self.microphone_combo.add_item(device.name, str(device.device_id))

            # Set current selection
            current_mic_id = self.settings_manager.get_selected_microphone_id()
            for i in range(len(self.microphone_combo.items)):
                if self.microphone_combo.items[i]["data"] == current_mic_id:
                    self.microphone_combo.set_current_index(i)
                    break
            else:
                # If current device not found, default to first item (usually "Default")
                if len(self.microphone_combo.items) > 0:
                    self.microphone_combo.set_current_index(0)

        except Exception as e:
            print(f"Error updating microphone dropdown: {e}")

    def on_microphone_changed(self, index: int):
        """Handle microphone selection change"""
        device_id = self.microphone_combo.current_data()
        device_name = self.microphone_combo.current_text()

        if device_id and device_name:
            self.settings_manager.set_selected_microphone(device_id, device_name)

    def on_refresh_devices(self):
        """Handle refresh button click"""
        print("Refreshing audio devices...")
        self.update_microphone_dropdown()

    def on_setting_changed(self, key: str, value: str):
        """Update UI when settings change externally"""
        if key == "selected_provider":
            # Update provider dropdown
            if value == "local":
                self.provider_combo.set_current_index(0)
            elif value == "openai":
                self.provider_combo.set_current_index(1)
            elif value == "groq":
                self.provider_combo.set_current_index(2)
            self.update_ui_for_provider()
        elif key.startswith("provider_api_key_"):
            # Update API key field if it matches current provider
            current_provider = self.settings_manager.get_selected_provider()
            if key == f"provider_api_key_{current_provider}":
                if self.api_key_input.text() != value:
                    self.api_key_input.setText(value)
        elif key in ["selected_microphone_id", "selected_microphone_name"]:
            # Update microphone dropdown if needed
            if key == "selected_microphone_id":
                current_mic_id = value
                for i in range(len(self.microphone_combo.items)):
                    if self.microphone_combo.items[i]["data"] == current_mic_id:
                        if self.microphone_combo.current_index != i:
                            self.microphone_combo.set_current_index(i)
                        break
