import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

class LoginScreen(QWidget):
    def __init__(self, auth_handler):
        super().__init__()
        self.auth_handler = auth_handler
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
        
        QTimer.singleShot(2000, lambda: self.authenticate_user(email, password))
    
    def authenticate_user(self, email, password):
        api_url = os.getenv("LOGIN_URL")
        if not api_url:
            QMessageBox.critical(self, "Configuration Error", "Authentication URL is not set!")
            self.reset_login_button()
            return
        
        data = {"email": email, "password": password}
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Login successful!")
                self.close()
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid credentials. Please try again.")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Login Error", f"Request failed: {e}")
        
        self.reset_login_button()
    
    def reset_login_button(self):
        self.login_button.setText("Login")
        self.login_button.setEnabled(True)

