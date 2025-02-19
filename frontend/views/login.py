import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer
from core.auth import AuthHandler

class LoginScreen(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.auth_handler = AuthHandler()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Hospital Management System")
        self.label.setFont(QFont("Arial", 14, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
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

        QTimer.singleShot(2000, lambda: self.authenticate(email, password))

    def authenticate(self, email, password):
        success, message, role = self.auth_handler.authenticate(email, password)

        if success:
            QMessageBox.information(self, "Login Success", f"Welcome, {role}!")
            self.close()
            self.on_login_success(role)
        else:
            QMessageBox.critical(self, "Login Failed", message)

        self.login_button.setText("Login")
        self.login_button.setEnabled(True)
