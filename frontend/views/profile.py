import os
from PySide6.QtWidgets import (QMessageBox, QWidget, QLabel, QHBoxLayout, QVBoxLayout, 
                              QGroupBox, QFormLayout, QPushButton, QLineEdit, QComboBox, QFileDialog,
                              QDateEdit, QFrame, QCheckBox, QSpinBox, QTabWidget)
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QTimer
import sys
from utils.api_utils import fetch_data, update_data, delete_data
from pathlib import Path
import base64
from datetime import datetime

class ProfileWindow(QWidget):  
    profile_updated = Signal(dict)
    picture_updated = Signal(str)
    settings_updated = Signal(dict)
    
    def __init__(self, user_role, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.user_role = user_role
        self.profile_pic_path = None
        self.user_info = None
        self.last_update_time = None
        
        # Initialize UI first
        self.setup_ui()
        
        # Then load data
        self.refresh_user_data()
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_for_updates)
        self.refresh_timer.start(900000)  # Check every 30 seconds

    def refresh_user_data(self):
        """Refresh user data from server"""
        self.user_info = self.fetch_user_info()
        if self.user_info:
            self.update_ui_with_user_data()
            self.last_update_time = datetime.now()
        else:
            QMessageBox.critical(self, "Error", "Cannot load profile data")
            self.close()

    def check_for_updates(self):
        """Check for server-side updates"""
        try:
            base_url = os.getenv("USER_URL")
            if not base_url:
                return

            api_url = f"{base_url}{self.user_id}/updates"
            
            params = {}
            if self.last_update_time:
                params['since'] = self.last_update_time.isoformat()
            
            response = fetch_data(self, api_url, self.token, params=params)
            if response and response.get('updated'):
                self.refresh_user_data()
                QMessageBox.information(self, "Updated", "Your profile has been updated with recent changes")
                
        except Exception as e:
            print(f"Update check failed: {e}")

    def fetch_user_info(self):
        """Fetch user information from the backend API."""
        base_url = os.getenv("USER_URL")
        if not base_url:
            QMessageBox.critical(self, "Error", "Configuration error: USER_URL not set")
            return None

        try:
            api_url = f"{base_url}user/{self.user_id}"
            
            response = fetch_data(self, api_url, self.token)
            if not response:
                return None

            # Process profile picture
            if 'profile_picture' in response and response['profile_picture']:
                if not response['profile_picture'].startswith('data:image'):
                    if isinstance(response['profile_picture'], bytes):
                        content_type = response.get('profile_picture_type', 'image/png')
                        base64_data = base64.b64encode(response['profile_picture']).decode('utf-8')
                        response['profile_picture'] = f"data:{content_type};base64,{base64_data}"
                    else:
                        response['profile_picture'] = "assets/icons/profile.png"
            else:
                response['profile_picture'] = "assets/icons/profile.png"

            return response

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {str(e)}")
            return None

    def setup_ui(self):
        """Initialize the UI components"""
        self.setWindowTitle("User Profile")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Status bar
        self.status_bar = QLabel("Loading...")
        self.status_bar.setAlignment(Qt.AlignRight)
        self.status_bar.setStyleSheet("color: #666; font-size: 12px;")
        
        # Header
        header = QHBoxLayout()
        title = QLabel("User Profile")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #007BFF;")
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setIcon(QIcon("assets/icons/refresh.png"))
        self.refresh_btn.clicked.connect(self.refresh_user_data)
        
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setIcon(QIcon("assets/icons/logout.png"))
        self.logout_btn.clicked.connect(self.logout_user)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.logout_btn)
        
        header.addWidget(title)
        header.addLayout(btn_layout)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Profile Tab
        self.profile_tab = QWidget()
        self.setup_profile_tab()
        
        # Settings Tab
        self.settings_tab = QWidget()
        self.setup_settings_tab()
        
        # Security Tab
        self.security_tab = QWidget()
        self.setup_security_tab()
        
        self.tabs.addTab(self.profile_tab, "Profile")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.security_tab, "Security")
        
        main_layout.addLayout(header)
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        self.apply_styles()
        
        # Connect signals
        self.profile_updated.connect(self.handle_profile_update)
        self.picture_updated.connect(self.handle_picture_update)
        self.settings_updated.connect(self.handle_settings_update)

    def update_ui_with_user_data(self):
        """Update UI elements with current user data"""
        if not self.user_info:
            return
            
        # Update status bar
        self.status_bar.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Update profile tab
        if hasattr(self, 'name_edit'):
            self.name_edit.setText(self.user_info.get('full_name', ''))
            self.email_edit.setText(self.user_info.get('email', ''))
            self.phone_edit.setText(self.user_info.get('contact_number', ''))
            self.address_edit.setText(self.user_info.get('address', ''))
            
            if self.user_role == "patient":
                self.dob_edit.setDate(self.user_info.get('date_of_birth', datetime.now().date()))
                gender = self.user_info.get('gender', 'Other')
                self.gender_combo.setCurrentText(gender)
        
        # Update profile picture
        self.load_profile_picture()
        
        # Update settings tab
        if hasattr(self, 'theme_combo'):
            theme = self.user_info.get('theme_preference', 'System')
            self.theme_combo.setCurrentText(theme)
            
            font_size = self.user_info.get('font_size', 14)
            self.font_size.setValue(font_size)
            
            notifications = self.user_info.get('notifications', {})
            self.email_notifs.setChecked(notifications.get('email', False))
            self.sms_notifs.setChecked(notifications.get('sms', False))
            self.push_notifs.setChecked(notifications.get('push', False))

    def setup_profile_tab(self):
        """Setup profile information tab"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Left side - Profile picture
        pic_frame = QFrame()
        pic_frame.setFixedWidth(250)
        pic_layout = QVBoxLayout()
        
        self.profile_pic = QLabel()
        self.profile_pic.setAlignment(Qt.AlignCenter)
        self.profile_pic.setFixedSize(200, 200)
        self.profile_pic.setStyleSheet("border: 2px solid #ddd; border-radius: 100px;")
        
        btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setIcon(QIcon("assets/icons/upload.png"))
        self.upload_btn.clicked.connect(self.upload_picture)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setIcon(QIcon("assets/icons/remove.png"))
        self.remove_btn.clicked.connect(self.remove_picture)
        
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.remove_btn)
        
        pic_layout.addWidget(self.profile_pic, 0, Qt.AlignCenter)
        pic_layout.addLayout(btn_layout)
        pic_frame.setLayout(pic_layout)
        
        # Right side - Personal info
        info_frame = QFrame()
        info_layout = QFormLayout()
        info_layout.setVerticalSpacing(15)
        
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(lambda: self.enable_save_btn(self.save_profile_btn))
        
        self.email_edit = QLineEdit()
        self.email_edit.textChanged.connect(lambda: self.enable_save_btn(self.save_profile_btn))
        
        self.phone_edit = QLineEdit()
        self.phone_edit.textChanged.connect(lambda: self.enable_save_btn(self.save_profile_btn))
        
        self.address_edit = QLineEdit()
        self.address_edit.textChanged.connect(lambda: self.enable_save_btn(self.save_profile_btn))
        
        info_layout.addRow("Full Name:", self.name_edit)
        info_layout.addRow("Email:", self.email_edit)
        info_layout.addRow("Phone:", self.phone_edit)
        info_layout.addRow("Address:", self.address_edit)
        
        # Save button
        self.save_profile_btn = QPushButton("Save Changes")
        self.save_profile_btn.setIcon(QIcon("assets/icons/save.png"))
        self.save_profile_btn.clicked.connect(self.save_personal_info)
        self.save_profile_btn.setEnabled(False)
        
        info_layout.addRow(self.save_profile_btn)
        info_frame.setLayout(info_layout)
        
        layout.addWidget(pic_frame)
        layout.addWidget(info_frame)
        self.profile_tab.setLayout(layout)

    def load_profile_picture(self):
        """Load profile picture from user info"""
        if not hasattr(self, 'user_info') or not self.user_info:
            return

        pic_data = self.user_info.get('profile_picture')
        
        if not pic_data:
            pixmap = QPixmap("assets/icons/profile.png")
        else:
            try:
                if pic_data.startswith('data:image'):
                    header, encoded = pic_data.split(',', 1)
                    image_data = base64.b64decode(encoded)
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                else:
                    pixmap = QPixmap(pic_data)
            except Exception as e:
                print(f"Error loading profile picture: {e}")
                pixmap = QPixmap("assets/icons/profile.png")
        
        if not pixmap.isNull():
            self.profile_pic.setPixmap(
                pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

    def upload_picture(self):
        """Handle profile picture upload"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                try:
                    with open(file_path, 'rb') as f:
                        image_data = f.read()
                    
                    extension = Path(file_path).suffix.lower()
                    content_type = f"image/{extension[1:]}"
                    
                    files = {'file': (os.path.basename(file_path), image_data, content_type)}
                    
                    base_url = os.getenv("USER_URL")
                    if not base_url:
                        QMessageBox.critical(self, "Error", "USER_URL not configured")
                        return
                    
                    api_url = f"{base_url}{self.user_id}/picture"
                    
                    # Show loading state
                    self.profile_pic.setPixmap(QPixmap("assets/icons/loading.png"))
                    
                    # Use a thread or async call in a real application
                    response = update_data(self, api_url, {}, self.token, files=files)
                    
                    if response and 'profile_picture' in response:
                        QMessageBox.information(self, "Success", "Profile picture updated!")
                        self.user_info['profile_picture'] = response['profile_picture']
                        self.load_profile_picture()
                        self.picture_updated.emit(response['profile_picture'])     
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update profile picture")
                        self.load_profile_picture()  # Revert to current picture
                        
                except Exception as e:
                    print("Error", f"Failed to upload picture: {str(e)}")
                    QMessageBox.critical(self, "Error", f"Failed to upload picture: {str(e)}")
                    self.load_profile_picture()

    def remove_picture(self):
        """Remove the current profile picture"""
        reply = QMessageBox.question(
            self, 'Confirm', 
            'Remove your profile picture?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            base_url = os.getenv("USER_URL")
            if not base_url:
                QMessageBox.critical(self, "Error", "USER_URL not configured")
                return
            
            api_url = f"{base_url}{self.user_id}/picture"
            
            if delete_data(self, api_url, self.token):
                self.user_info['profile_picture'] = None
                self.load_profile_picture()
                self.picture_updated.emit("")
                QMessageBox.information(self, "Success", "Profile picture removed")

    def save_personal_info(self):
        """Save personal information changes"""
        if not self.validate_personal_info():
            return
            
        updated_data = {
            "full_name": self.name_edit.text(),
            "email": self.email_edit.text(),
            "contact_number": self.phone_edit.text(),
            "address": self.address_edit.text()
        }
        
               
        base_url = os.getenv("USER_URL")
        if not base_url:
            QMessageBox.critical(self, "Error", "USER_URL not configured")
            return
            
        api_url = f"{base_url}staff/{self.user_id}/update"
        
        # Show loading state
        self.save_profile_btn.setText("Saving...")
        self.save_profile_btn.setEnabled(False)
        
        response = update_data(self, api_url, updated_data, self.token)
        
        if response:
            self.user_info.update(response)
            self.save_profile_btn.setText("Save Changes")
            self.save_profile_btn.setEnabled(False)
            self.profile_updated.emit(response)
            QMessageBox.information(self, "Success", "Profile updated successfully!")
        else:
            self.save_profile_btn.setText("Save Changes")
            self.save_profile_btn.setEnabled(True)
            QMessageBox.critical(self, "Error", "Failed to update profile")

    def validate_personal_info(self):
        """Validate personal info before saving"""
        errors = []
        
        if not self.name_edit.text().strip():
            errors.append("Full name is required")
            
        if not self.email_edit.text().strip():
            errors.append("Email is required")
        elif "@" not in self.email_edit.text():
            errors.append("Valid email is required")
            
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return False
            
        return True

    def enable_save_btn(self, button):
        """Enable save button when changes are detected"""
        if not hasattr(self, 'user_info') or not self.user_info:
            return
            
        changed = False
        
        # Check profile fields
        if (self.name_edit.text() != self.user_info.get('full_name', '') or
            self.email_edit.text() != self.user_info.get('email', '') or
            self.phone_edit.text() != self.user_info.get('contact_number', '') or
            self.address_edit.text() != self.user_info.get('address', '')):
            changed = True
            
        
                
        button.setEnabled(changed)

    def setup_settings_tab(self):
        """Setup account settings tab"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Notification Settings
        notif_group = QGroupBox("Notification Preferences")
        notif_layout = QVBoxLayout()
        
        self.email_notifs = QCheckBox("Email Notifications")
        self.sms_notifs = QCheckBox("SMS Notifications")
        self.push_notifs = QCheckBox("Push Notifications")
        
        notif_layout.addWidget(self.email_notifs)
        notif_layout.addWidget(self.sms_notifs)
        notif_layout.addWidget(self.push_notifs)
        notif_group.setLayout(notif_layout)
        
        # Display Settings
        display_group = QGroupBox("Display Preferences")
        display_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(lambda: self.enable_save_btn(self.save_settings_btn))
        
        self.font_size = QSpinBox()
        self.font_size.setRange(10, 24)
        self.font_size.valueChanged.connect(lambda: self.enable_save_btn(self.save_settings_btn))
        
        display_layout.addRow("Theme:", self.theme_combo)
        display_layout.addRow("Font Size:", self.font_size)
        display_group.setLayout(display_layout)
        
        # Save Button
        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.setIcon(QIcon("assets/icons/save.png"))
        self.save_settings_btn.clicked.connect(self.save_settings)
        self.save_settings_btn.setEnabled(False)
        
        layout.addWidget(notif_group)
        layout.addWidget(display_group)
        layout.addStretch()
        layout.addWidget(self.save_settings_btn, 0, Qt.AlignRight)
        
        self.settings_tab.setLayout(layout)

    def setup_security_tab(self):
        """Setup security settings tab"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Password Change
        pass_group = QGroupBox("Change Password")
        pass_layout = QVBoxLayout()
        
         # Add the change password button
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.setIcon(QIcon("assets/icons/password.png"))
        self.change_password_button.clicked.connect(self.open_change_password)
        pass_layout.addWidget(self.change_password_button)
        pass_group.setLayout(pass_layout)
        
        # Security Questions
        sec_group = QGroupBox("Security Questions")
        sec_layout = QFormLayout()
        
        self.sec_question1 = QComboBox()
        self.sec_question1.addItems([
            "What was your first pet's name?",
            "What city were you born in?",
            "What was your first school?"
        ])
        
        self.sec_answer1 = QLineEdit()
        self.sec_answer1.setPlaceholderText("Your answer")
        
        sec_layout.addRow("Question 1:", self.sec_question1)
        sec_layout.addRow("Answer:", self.sec_answer1)
        sec_group.setLayout(sec_layout)
        
        layout.addWidget(pass_group)
        layout.addWidget(sec_group)
        layout.addStretch()
        
        self.security_tab.setLayout(layout)

    def save_settings(self):
        """Save account settings"""
        settings = {
            "notifications": {
                "email": self.email_notifs.isChecked(),
                "sms": self.sms_notifs.isChecked(),
                "push": self.push_notifs.isChecked()
            },
            "theme": self.theme_combo.currentText(),
            "font_size": self.font_size.value()
        }
        
        base_url = os.getenv("USER_URL")
        if not base_url:
            QMessageBox.critical(self, "Error", "USER_URL not configured")
            return
            
        api_url = f"{base_url}user/{self.user_id}/settings"
        
        # Show loading state
        self.save_settings_btn.setText("Saving...")
        self.save_settings_btn.setEnabled(False)
        
        response = update_data(self, api_url, settings, self.token)
        
        if response:
            self.user_info.update(response.get('settings', {}))
            self.save_settings_btn.setText("Save Settings")
            self.save_settings_btn.setEnabled(False)
            self.settings_updated.emit(response)
            QMessageBox.information(self, "Success", "Settings updated successfully!")
        else:
            self.save_settings_btn.setText("Save Settings")
            self.save_settings_btn.setEnabled(True)
            QMessageBox.critical(self, "Error", "Failed to update settings")

    
    def open_change_password(self):
        """Open the Change Password window."""
        from .change_password import ChangePasswordWindow
        self.change_password_window = ChangePasswordWindow(self.token)
        self.change_password_window.show()

    def handle_profile_update(self, updated_data):
        """Handle profile update signal"""
        self.user_info.update(updated_data)
        self.status_bar.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.save_profile_btn.setEnabled(False)

    def handle_picture_update(self, picture_data):
        """Handle picture update signal"""
        self.user_info['profile_picture'] = picture_data
        self.status_bar.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def handle_settings_update(self, updated_data):
        """Handle settings update signal"""
        self.user_info.update(updated_data.get('settings', {}))
        self.status_bar.setText(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.save_settings_btn.setEnabled(False)

    def closeEvent(self, event):
        """Handle window close"""
        self.refresh_timer.stop()
        event.accept()

    def apply_styles(self):
        """Apply consistent styling to all components"""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
            QTabWidget::pane {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 8px 15px;
                border-radius: 3px;
                background: #f0f0f0;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0078D7;
                color: white;
            }
            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
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
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dcdcdc;
                padding: 15px;
            }
            QLineEdit, QComboBox, QSpinBox, QDateEdit {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
                border: 1px solid #007BFF;
            }
            QCheckBox {
                spacing: 5px;
            }
        """)

    def logout_user(self):
        """Handle user logout"""
        reply = QMessageBox.question(
            self, 'Logout', 
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.close()
            python = sys.executable
            os.execl(python, python, "main.py")