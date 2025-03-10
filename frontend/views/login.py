import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QHBoxLayout
)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt, QTimer
from core.auth import AuthHandler

class LoginScreen(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.auth_handler = AuthHandler()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with modern styling."""
        self.setWindowTitle("Login - Hospital Management System")
        self.setGeometry(100, 100, 400, 450)
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

        # Logo Section
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/icons/hospital.png")  # Replace with actual logo path
        logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel("Hospital Management System")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form Fields
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # Footer
        footer_label = QLabel("© 2025 Hospital System - All Rights Reserved")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(footer_label)

        self.setLayout(layout)

    def handle_login(self):
        """Handle login process with input validation."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Validation Error", "Email and password cannot be empty!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address!")
            return

        self.login_button.setText("Logging in...")
        self.login_button.setEnabled(False)

        QTimer.singleShot(1500, lambda: self.authenticate(email, password))

    def authenticate(self, email, password):
        """Authenticate user with backend API."""
        success, message, role = self.auth_handler.authenticate(email, password)

        if success:
            QMessageBox.information(self, "Login Success", f"Welcome, {role}!")
            self.close()
            self.on_login_success(role)
        else:
            QMessageBox.critical(self, "Login Failed", message)

        self.login_button.setText("Login")
        self.login_button.setEnabled(True)
