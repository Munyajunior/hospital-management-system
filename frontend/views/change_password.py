from PySide6.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QFrame
)
from PySide6.QtGui import QIcon
from utils.api_utils import post_data
import os

class ChangePasswordWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI with modern styling."""
        self.setWindowTitle("Change Password")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #007BFF;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdcdc;
                padding: 20px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Form Container
        form_container = QFrame()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        # Current Password
        self.current_password_label = QLabel("Current Password:")
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.current_password_input.setPlaceholderText("Enter your current password")
        form_layout.addWidget(self.current_password_label)
        form_layout.addWidget(self.current_password_input)

        # New Password
        self.new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("Enter your new password")
        form_layout.addWidget(self.new_password_label)
        form_layout.addWidget(self.new_password_input)

        # Confirm New Password
        self.confirm_password_label = QLabel("Confirm New Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm your new password")
        form_layout.addWidget(self.confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("Change Password")
        self.submit_button.setIcon(QIcon("assets/icons/password.png"))
        self.submit_button.clicked.connect(self.change_password)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(QIcon("assets/icons/cancel.png"))
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        form_layout.addLayout(button_layout)
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def change_password(self):
        """Handle password change process."""
        current_password = self.current_password_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # Input Validation
        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "New passwords do not match!")
            return

        if len(new_password) < 8:
            QMessageBox.warning(self, "Error", "New password must be at least 8 characters long!")
            return

        # Send request to the backend
        api_url = os.getenv("CHANGE_PASSWORD_URL")
        data = {"current_password": current_password, "new_password": new_password}
        
        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Password changed successfully!")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to change password. Check your current password.")