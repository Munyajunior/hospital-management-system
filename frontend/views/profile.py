import os
from PySide6.QtWidgets import (QMessageBox, QWidget, QLabel, QHBoxLayout, QVBoxLayout, 
                              QGroupBox, QFormLayout, QPushButton, QLineEdit, QComboBox, QFileDialog)
from PySide6.QtGui import QFont, QPixmap, QIcon, QImage
from PySide6.QtCore import Qt, Signal
import sys
from utils.api_utils import fetch_data, update_data
from pathlib import Path
import base64

class ProfileWindow(QWidget):  
    profile_updated = Signal(dict)  # Signal to notify when profile is updated
    
    def __init__(self, user_role, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.user_role = user_role
        self.profile_pic_path = None
        self.user_info = self.fetch_user_info()
        self.setup_ui()

    def fetch_user_info(self):
        """Fetch user information from the backend API."""
        base_url = os.getenv("USER_URL")
        if self.user_role == "patient":
            api_url = f"{base_url}patient/{self.user_id}"
        else:
            api_url = f"{base_url}user/{self.user_id}"
        
        response = fetch_data(self, api_url, self.token)
        if not response:
            QMessageBox.critical(self, "Error", "Failed to fetch user information.")
            return None
        
        # Set default profile picture if none exists
        if not response.get("profile_picture"):
            response["profile_picture"] = "assets/icons/profile.png"
        return response

    def setup_ui(self):
        """Initialize the UI with modern styling and editable fields."""
        self.setWindowTitle("User Profile")
        self.setGeometry(100, 100, 700, 500)
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
                padding: 8px;
                font-size: 14px;
                min-width: 100px;
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
            QLineEdit, QComboBox {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #007BFF;
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

        # Action Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Changes")
        self.save_button.setIcon(QIcon("assets/icons/save.png"))
        self.save_button.clicked.connect(self.save_profile)
        self.save_button.setEnabled(False)
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.setIcon(QIcon("assets/icons/logout.png"))
        self.logout_button.clicked.connect(self.logout_user)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.logout_button)
        header_layout.addLayout(button_layout)
        main_layout.addLayout(header_layout)

        # Profile Content
        content_layout = QHBoxLayout()
        
        # Left Column - Profile Picture
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setAlignment(Qt.AlignCenter)
        self.load_profile_picture()
        
        self.change_pic_button = QPushButton("Change Picture")
        self.change_pic_button.setIcon(QIcon("assets/icons/image.png"))
        self.change_pic_button.clicked.connect(self.change_profile_picture)
        
        left_column.addWidget(self.profile_pic_label)
        left_column.addWidget(self.change_pic_button)
        
        # Right Column - User Details
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        
        # Personal Information Section
        personal_group = QGroupBox("Personal Information")
        personal_layout = QFormLayout()
        personal_layout.setSpacing(10)
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.user_info.get('full_name', ''))
        self.name_edit.textChanged.connect(self.enable_save_button)
        
        self.email_edit = QLineEdit()
        self.email_edit.setText(self.user_info.get('email', ''))
        self.email_edit.textChanged.connect(self.enable_save_button)
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setText(self.user_info.get('contact_number', ''))
        self.phone_edit.textChanged.connect(self.enable_save_button)
        
        self.address_edit = QLineEdit()
        self.address_edit.setText(self.user_info.get('address', ''))
        self.address_edit.textChanged.connect(self.enable_save_button)
        
        personal_layout.addRow("Full Name:", self.name_edit)
        personal_layout.addRow("Email:", self.email_edit)
        personal_layout.addRow("Phone:", self.phone_edit)
        personal_layout.addRow("Address:", self.address_edit)
        
        if self.user_role == "patient":
            self.dob_edit = QLineEdit()
            self.dob_edit.setText(str(self.user_info.get('date_of_birth', '')))
            self.dob_edit.textChanged.connect(self.enable_save_button)
            personal_layout.addRow("Date of Birth:", self.dob_edit)
            
            self.gender_combo = QComboBox()
            self.gender_combo.addItems(["Male", "Female", "Other"])
            gender = self.user_info.get('gender', '')
            if gender:
                self.gender_combo.setCurrentText(gender)
            self.gender_combo.currentTextChanged.connect(self.enable_save_button)
            personal_layout.addRow("Gender:", self.gender_combo)
        
        personal_group.setLayout(personal_layout)
        right_column.addWidget(personal_group)
        
        # Account Settings Section
        account_group = QGroupBox("Account Settings")
        account_layout = QVBoxLayout()
        
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.setIcon(QIcon("assets/icons/password.png"))
        self.change_password_button.clicked.connect(self.open_change_password)
        
        account_layout.addWidget(self.change_password_button)
        account_group.setLayout(account_layout)
        right_column.addWidget(account_group)
        
        content_layout.addLayout(left_column, 30)
        content_layout.addLayout(right_column, 70)
        main_layout.addLayout(content_layout)

        # Footer
        footer_label = QLabel("© 2025 Hospital System - All Rights Reserved")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("font-size: 12px; color: #888;")
        main_layout.addWidget(footer_label)

        self.setLayout(main_layout)

    def load_profile_picture(self):
        """Load the profile picture from the user info or default."""
        pic_data = self.user_info.get('profile_picture')
        
        if pic_data and pic_data.startswith('data:image'):
             # Handle base64 encoded image
            try:
                header, encoded = pic_data.split(',', 1)
                image_data = base64.b64decode(encoded)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                self.profile_pic_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
            except Exception as e:
                print(f"Error loading profile picture: {e}")
        
        # Fallback to default image
        pixmap = QPixmap("assets/icons/profile.png")
        self.profile_pic_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    def change_profile_picture(self):
        """Open a file dialog to select a new profile picture."""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.profile_pic_path = selected_files[0]
                pixmap = QPixmap(self.profile_pic_path)
                if not pixmap.isNull():
                    self.profile_pic_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.enable_save_button()

    def enable_save_button(self):
        """Enable the save button when changes are detected."""
        self.save_button.setEnabled(True)

    def save_profile(self):
        """Save the updated profile information to the backend."""
        # Prepare form data for multipart upload
        files = {}
        updated_data = {
            "full_name": self.name_edit.text(),
            "email": self.email_edit.text(),
            "contact_number": self.phone_edit.text(),
            "address": self.address_edit.text()
        }
        
        if self.user_role == "patient":
            updated_data.update({
                "date_of_birth": self.dob_edit.text(),
                "gender": self.gender_combo.currentText()
            })
        
        # Handle profile picture upload
        if self.profile_pic_path:
            try:
                # Open the image file and prepare for upload
                with open(self.profile_pic_path, "rb") as f:
                    files["profile_picture"] = (
                        os.path.basename(self.profile_pic_path),
                        f.read(),
                        f"image/{Path(self.profile_pic_path).suffix[1:]}"
                    )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to process image: {str(e)}")
                return
        
        # Determine API endpoint based on user role
        base_url = os.getenv("USER_URL")
        if self.user_role == "patient":
            api_url = f"{base_url}patients/{self.user_id}/update"
        else:
            api_url = f"{base_url}staff/{self.user_id}/update"
        
        # Send update request
        response = update_data(self, api_url, updated_data, self.token, files=files if files else None)
        
        if response:
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.user_info.update(response)
            self.save_button.setEnabled(False)
            self.profile_updated.emit(self.user_info)
        else:
            QMessageBox.critical(self, "Error", "Failed to update profile.")

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