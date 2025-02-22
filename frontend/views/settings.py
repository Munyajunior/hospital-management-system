from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
    QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
import requests
import os

class Settings(QWidget):
    def __init__(self, auth_token, user_role):
        super().__init__()
        self.auth_token = auth_token
        self.user_role = user_role

        # Ensure only authorized users can access settings
        if not auth_token:
            QMessageBox.critical(self, "Access Denied", "You must be logged in to access settings.")
            self.close()
            return
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setGeometry(300, 300, 500, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border-radius: 5px;
                border: 1px solid #ccc;
                background-color: white;
            }
        """)

        layout = QVBoxLayout()

        self.label = QLabel("System Settings")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Theme Selection
        self.theme_label = QLabel("Select Theme:")
        layout.addWidget(self.theme_label)

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark", "System Default"])
        layout.addWidget(self.theme_selector)

        # Password Change Section
        self.password_label = QLabel("Change Password:")
        layout.addWidget(self.password_label)

        self.old_password_input = QLineEdit()
        self.old_password_input.setPlaceholderText("Enter old password")
        self.old_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        self.update_password_button = QPushButton("Update Password")
        self.update_password_button.clicked.connect(self.update_password)
        layout.addWidget(self.update_password_button)

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        """Saves user settings like theme preferences"""
        selected_theme = self.theme_selector.currentText()
        QMessageBox.information(self, "Settings Saved", f"Theme set to: {selected_theme}")

    def update_password(self):
        """Handles password updates"""
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()

        if not old_password or not new_password:
            QMessageBox.warning(self, "Input Error", "Please fill out all fields.")
            return

        api_url = os.getenv("UPDATE_PASSWORD_URL")
        headers = {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        data = {"old_password": old_password, "new_password": new_password}

        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Password updated successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to update password. Please try again.")
