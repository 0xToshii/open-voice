from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class DeleteConfirmationDialog(QDialog):
    """Custom delete confirmation dialog matching the design"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the dialog UI to match the design"""
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(400, 160)

        # Remove window decorations to create custom dialog
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)

        # Title
        title_label = QLabel("Delete from history")
        title_label.setObjectName("dialogTitle")
        main_layout.addWidget(title_label)

        # Subtitle/description
        desc_label = QLabel("This action cannot be undone.")
        desc_label.setObjectName("dialogDescription")
        main_layout.addWidget(desc_label)

        # Add some spacing before buttons
        main_layout.addSpacing(12)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(12)

        button_layout.addStretch()

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setFixedSize(80, 32)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        # Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setFixedSize(80, 32)
        self.delete_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.delete_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def apply_styles(self):
        """Apply custom styles to match the design"""
        style = """
        QDialog {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }
        
        #closeButton {
            background-color: transparent;
            border: none;
            color: #999999;
            font-size: 18px;
            font-weight: normal;
            border-radius: 12px;
        }
        
        #closeButton:hover {
            background-color: #f0f0f0;
            color: #666666;
        }
        
        #dialogTitle {
            font-size: 18px;
            font-weight: 600;
            color: #333333;
            background-color: transparent;
            margin: 0px;
            padding: 0px;
        }
        
        #dialogDescription {
            font-size: 14px;
            color: #666666;
            background-color: transparent;
            margin: 0px;
            padding: 0px;
        }
        
        #cancelButton {
            background-color: #ffffff;
            border: 1px solid #d0d0d0;
            color: #333333;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
        }
        
        #cancelButton:hover {
            background-color: #f8f8f8;
            border-color: #c0c0c0;
        }
        
        #cancelButton:pressed {
            background-color: #f0f0f0;
        }
        
        #deleteButton {
            background-color: #e74c3c;
            border: 1px solid #e74c3c;
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
            border-radius: 6px;
        }
        
        #deleteButton:hover {
            background-color: #c0392b;
            border-color: #c0392b;
        }
        
        #deleteButton:pressed {
            background-color: #a93226;
        }
        """

        self.setStyleSheet(style)

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.accept()
        else:
            super().keyPressEvent(event)
