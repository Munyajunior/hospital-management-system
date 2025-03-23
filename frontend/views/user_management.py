from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QComboBox, QToolButton,
    QLineEdit, QHeaderView, QApplication,QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.api_utils import fetch_data, post_data, delete_data, update_data
import os

class UserManagement(QWidget):
    def __init__(self, role, user_id, auth_token):
        super().__init__()
        self.token = auth_token
        self.role = role
        self.user_id = user_id

        # Enforce authentication
        if not auth_token:
            QMessageBox.critical(self, "Access Denied", "You must be logged in to access this page.")
            self.close()
            return
        
        if role not in ["admin"]:
            QMessageBox.critical(self, "Access Denied", "You do not have permission to access this module.")
            self.close()
            return
        
        self.init_ui()
        self.load_users()

    def init_ui(self):
        self.setWindowTitle("User Management")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(800, 600)  # Set a reasonable minimum size
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
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
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
        """)

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Users")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Name", "Role", "Is Active","Activate/Deactivate", "Delete"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)
        self.duplicate_header()

        if self.role == "admin":  
            self.add_user_section(layout)
            self.update_user_section(layout)

        self.refresh_button = QPushButton("Refresh Users")
        self.refresh_button.clicked.connect(self.load_users)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        
    def duplicate_header(self):
        """Adds a duplicate header at the bottom of the table."""
        self.user_table.setRowCount(self.user_table.rowCount() + 1)
        for col in range(self.user_table.columnCount()):
            item = QTableWidgetItem(self.user_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.user_table.setItem(self.user_table.rowCount() - 1, col, item)
            
    def add_user_section(self, layout):
        """Admin-only section for adding new users."""
        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        form_layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter a valid email")
        form_layout.addWidget(self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.password_input)

        # Toggle Password Visibility Button
        self.toggle_password_button = QToolButton()
        self.toggle_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))  # Default icon for hidden password
        self.toggle_password_button.setCheckable(True)  # Make the button toggleable
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.toggle_password_button)

        
        self.role_select = QComboBox()
        self.role_select.addItems(["select", "doctor", "nurse", "pharmacist", "lab_technician", "radiologist", "admin", "icu"])
        form_layout.addWidget(self.role_select)

        self.add_user_button = QPushButton("Add User")
        self.add_user_button.clicked.connect(self.add_user)
        form_layout.addWidget(self.add_user_button)

        layout.addLayout(form_layout)
        
    def update_user_section(self , layout):
        """Change user's Login information."""
        update_group = QGroupBox("Update User")
        update_layout = QFormLayout()

        self.new_email_input = QLineEdit()
        self.new_email_input.setPlaceholderText("Enter new email")
        update_layout.addRow("New Email:", self.new_email_input)

        password_layout = QHBoxLayout()

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.new_password_input)

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
        password_layout.addWidget(self.toggle_password_button)

        update_layout.addRow("Password:", password_layout)
        
        self.update_user_button = QPushButton("Update User")
        self.update_user_button.clicked.connect(self.update_user_info)
        update_layout.addRow(self.update_user_button)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)
    
    def update_user_info(self):
        """Handles updating a user."""
        selected_row = self.user_table.currentRow()
        if selected_row < 1:  # Skip the header row
            QMessageBox.warning(self, "Selection Error", "Please select a user from the table.")
            return

        user_id = int(self.user_table.item(selected_row, 0).text())
        new_email = self.new_email_input.text().strip()
        new_password = self.new_password_input.text().strip()

        if not new_email or "@" not in new_email:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return
        if not new_password or len(new_password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return
            
        api_url = os.getenv("USER_URL") + f"{user_id}/update"
        data = {"email": new_email,
                "password": new_password}
        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "User updated successfully.")
            self.new_email_input.clear()
            self.new_password_input.clear()
            self.load_users() 
        else:
            QMessageBox.critical(self, "Error", "Failed to update User.")

    def load_users(self):
        """Fetches user data from the backend API."""
        api_url = os.getenv("USER_URL")
        users = fetch_data(self, api_url, self.token)
        if users:
            # Clear the table and add a row for the duplicate header
            self.user_table.setRowCount(0)  # Clear all rows
            self.user_table.insertRow(0)  # Insert a new row at the top for the duplicate header

            # Add the duplicate header at row 0
            for col in range(self.user_table.columnCount()):
                item = QTableWidgetItem(self.user_table.horizontalHeaderItem(col).text())
                item.setBackground(Qt.gray)
                item.setForeground(Qt.white)
                self.user_table.setItem(0, col, item)

            # Populate the table with data starting from row 1
            for row, user in enumerate(users, start=1):  # Start from row 1
                self.user_table.insertRow(row)
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
                self.user_table.setItem(row, 1, QTableWidgetItem(user["full_name"]))
                self.user_table.setItem(row, 2, QTableWidgetItem(user["role"]))
                self.user_table.setItem(row, 3, QTableWidgetItem(str(user["is_active"])))

                if self.role == "admin":
                    # Activate/Deactivate Button
                    activate_deactivate_button = QPushButton("Deactivate" if user["is_active"] else "Activate")
                    activate_deactivate_button.setStyleSheet("background-color: #ffc107; color: white; border-radius: 5px;")
                    activate_deactivate_button.clicked.connect(
                        lambda _, u_id=user["id"], u_active=str(user["is_active"]).lower(): self.update_user(u_id, u_active)
                    )
                    self.user_table.setCellWidget(row, 4, activate_deactivate_button)

                    # Delete Button
                    delete_button = QPushButton("Delete")
                    delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
                    delete_button.clicked.connect(lambda _, u_id=user["id"]: self.delete_user(u_id))
                    self.user_table.setCellWidget(row, 5, delete_button)
        else:
            QMessageBox.critical(self, "Error", "Failed to load user data.")

    def add_user(self):
        """Handles adding a new user (Admin only)."""
        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_select.currentText().strip()

        if not full_name or not email or not password or not role:
            QMessageBox.warning(self, "Input Error", "All field are required.")
            return
        if role == "select":
            QMessageBox.warning(self, "Input Error", "Please select a valid role")
            return
        if "@" not in email:
            QMessageBox.warning(self, "Input Error", "Please Enter a valid email Address.")
            return
        if len(password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return
            
        api_url = os.getenv("ADD_USER_URL")
        data = {
            "full_name": full_name, 
            "email":email,
            "password":password,
            "role": role
            }
        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "User added successfully.")
            self.load_users()
            self.name_input.clear()
            self.email_input.clear()
            self.password_input.clear()
            self.role_select.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Error", "Failed to add user.")

    def delete_user(self, user_id):
        """Handles user deletion (Admin only)."""
        base_url = os.getenv("USER_URL")
        api_url = f"{base_url}{user_id}"
        response = delete_data(self, api_url, self.token)
        if response:
            QMessageBox.information(self, "Success", "User deleted successfully.")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", "Failed to delete user.")
            
    def update_user(self, user_id, is_active):
        """Handles user activation/deactivation (Admin only)."""
        base_url = os.getenv("USER_URL")
        api_url = f"{base_url}{user_id}/is_active"

        # Convert is_active to a boolean
        is_active_bool = is_active.lower() == "true"  # Convert string to boolean

        # Toggle the is_active status
        new_status = not is_active_bool

        # Prepare the data for the API request
        data = {"is_active": new_status}

        # Send the update request
        response = update_data(self, api_url, data, self.token)

        if response:
            message = "User activated successfully." if new_status else "User deactivated successfully."
            QMessageBox.information(self, "Success", message)
            self.load_users()  # Refresh the user table
        else:
            QMessageBox.critical(self, "Error", "Failed to update user status.")
    
    def toggle_password_visibility(self):
        """Toggles the visibility of the password field."""
        if self.toggle_password_button.isChecked():
            # Show password
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.new_password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setIcon(QIcon("assets/icons/eye.png"))  # Icon for visible password
        else:
            # Hide password
            self.password_input.setEchoMode(QLineEdit.Password)
            self.new_password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))  # Icon for hidden password
        