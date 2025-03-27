import os
from PySide6.QtWidgets import QMessageBox, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QMainWindow
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt
import sys
from utils.api_utils import fetch_data

class ProfileWindow(QWidget):  
    def __init__(self, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.user_info = self.fetch_user_info()
        self.setup_ui()

    def fetch_user_info(self):
        """Fetch user information from the backend API."""
        base_url = os.getenv("USER_URL")
        api_url = f"{base_url}user/{self.user_id}"
        
        response = fetch_data(self, api_url, self.token)
        if not response:
            QMessageBox.critical(self, "Error", "Failed to fetch user information.")
            return None
        return response

    def setup_ui(self):
        """Initialize the UI with modern styling."""
        self.setWindowTitle("User Profile")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
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
                padding: 15px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Section
        header_layout = QHBoxLayout()
        header_label = QLabel("User Profile")
        header_label.setFont(QFont("Arial", 20, QFont.Bold))
        header_label.setStyleSheet("color: #007BFF;")
        header_layout.addWidget(header_label)

        # Logout Button
        self.logout_button = QPushButton("Logout")
        self.logout_button.setIcon(QIcon("assets/icons/logout.png"))
        self.logout_button.clicked.connect(self.logout_user)
        header_layout.addWidget(self.logout_button, alignment=Qt.AlignRight)
        main_layout.addLayout(header_layout)

        # User Information Card
        user_card = QFrame()
        user_card_layout = QVBoxLayout()
        user_card_layout.setSpacing(15)

        name_role = (f"{self.user_info.get("role","N/A")}.{self.user_info.get("full_name","N/A")}")
        
        # Profile Picture
        profile_pic_label = QLabel()
        welcome_label = QLabel(f"Welcome ")
        welcome_label.setStyleSheet("""
                                    border:none;
                                    font-size:16px;
                                    font-weight: bold;
                                    """)
        welcome_label.setAlignment(Qt.AlignCenter)
        profile_pic_label.setPixmap(QPixmap("assets/icons/profile.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        profile_pic_label.setStyleSheet("font-size:16px;")
        profile_pic_label.setAlignment(Qt.AlignCenter)
        user_card_layout.addWidget(welcome_label)
        user_card_layout.addWidget(profile_pic_label)

        # User Details
        self.name_label = QLabel(f"Name: {self.user_info.get('full_name', 'N/A')}")
        self.name_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.email_label = QLabel(f"Email: {self.user_info.get('email', 'N/A')}")
        self.role_label = QLabel(f"Role: {self.user_info.get('role', 'N/A')}")

        user_card_layout.addWidget(self.name_label)
        user_card_layout.addWidget(self.email_label)
        user_card_layout.addWidget(self.role_label)

        # Change Password Button
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.setIcon(QIcon("assets/icons/password.png"))
        self.change_password_button.clicked.connect(self.open_change_password)
        user_card_layout.addWidget(self.change_password_button)

        user_card.setLayout(user_card_layout)
        main_layout.addWidget(user_card)

        # Footer
        footer_label = QLabel("© 2025 Hospital System - All Rights Reserved")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 12px; color: #888;")
        main_layout.addWidget(footer_label)

        # Set the layout directly
        self.setLayout(main_layout)  

    def open_change_password(self):
        """Open the Change Password window."""
        from .change_password import ChangePasswordWindow
        self.change_password_window = ChangePasswordWindow(self.token)
        self.change_password_window.show()

    def logout_user(self):
        """Log out the user and close the profile window."""
        QMessageBox.information(self, "Logout", "You have been logged out.")
        self.token = None
        self.user_id = None
        python = sys.executable
        os.execl(python, python, "main.py")