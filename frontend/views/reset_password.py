from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QToolButton
from PySide6.QtGui import QIcon
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class ResetPasswordPage(QWidget):
    def __init__(self, token):
        super().__init__()
        self.setWindowTitle("Reset Password")
        self.setGeometry(400, 200, 400, 250)
        self.token = token

        layout = QVBoxLayout()

        self.label = QLabel("Enter your new password:")
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("New Password")
        layout.addWidget(self.password_input)
        
        # Toggle Password Visibility Button
        self.toggle_password_button = QToolButton()
        self.toggle_password_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                color: #4CAF5F;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                text-decoration: underline;
                padding: 5px;
            }
            QToolButton:checked{
                background-color: #f44336;
            }
            QToolButton:hover {
                background-color: #45a049;
            }
            QToolButton:pressed {
                background-color: #367c39;
            }
        """)
        self.toggle_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))  # Default icon for hidden password
        self.toggle_password_button.setCheckable(True)  # Make the button toggleable
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.toggle_password_button)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        layout.addWidget(self.confirm_password_input)

        self.submit_button = QPushButton("Reset Password")
        self.submit_button.clicked.connect(self.reset_password)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def reset_password(self):
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not password or not confirm_password:
            QMessageBox.warning(self, "Input Error", "Please enter and confirm your password!")
            return
        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match!")
            return
        if len(password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long!")
            return

        try:
            response = requests.post(os.getenv("RESET_PASSWORD_URL"), json={
                "token": self.token,
                "new_password": password
            })

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Password reset successfully!")
                self.close()
            else:
                QMessageBox.warning(self, "Error", response.json().get("detail", "Something went wrong"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send request: {str(e)}")

    def toggle_password_visibility(self):
        """Toggles the visibility of the password field."""
        if self.toggle_password_button.isChecked():
            # Show password
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setIcon(QIcon("assets/icons/eye.png"))  # Icon for visible password
        else:
            # Hide password
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))  # Icon for hidden password
        