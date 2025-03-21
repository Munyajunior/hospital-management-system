from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class ForgotPasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forgot Password")
        self.setGeometry(400, 200, 400, 250)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #666;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #444;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Reset Your Password")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Email Input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.email_input)

        # Submit Button
        self.submit_button = QPushButton("Send Reset Link")
        self.submit_button.clicked.connect(self.send_reset_request)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def send_reset_request(self):
        """Send a password reset request to the backend."""
        email = self.email_input.text().strip()

        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Error", "Please enter a valid email address!")
            return

        self.submit_button.setText("Sending...")
        self.submit_button.setEnabled(False)

        try:
            # Send request to the backend
            response = requests.post(
                os.getenv("FORGOT_PASSWORD_RESET_URL"),
                json={"email": email}
            )

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "A reset link has been sent to your email.")
                self.close()
            else:
                QMessageBox.warning(self, "Error", f"{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send request: {str(e)}")
        finally:
            self.submit_button.setText("Send Reset Link")
            self.submit_button.setEnabled(True)