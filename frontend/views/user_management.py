from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QComboBox, 
    QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, post_data, delete_data
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
        self.setGeometry(300, 300, 900, 600)
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
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Name", "Role", "Is Active","Actions"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)

        if self.role == "admin":  
            self.add_user_section(layout)

        self.refresh_button = QPushButton("Refresh Users")
        self.refresh_button.clicked.connect(self.load_users)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

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
        
        self.role_select = QComboBox()
        self.role_select.addItems(["select", "doctor", "nurse", "pharmacist", "lab_technician", "radiologist", "admin", "icu"])
        form_layout.addWidget(self.role_select)

        self.add_user_button = QPushButton("Add User")
        self.add_user_button.clicked.connect(self.add_user)
        form_layout.addWidget(self.add_user_button)

        layout.addLayout(form_layout)

    def load_users(self):
        """Fetches user data from the backend API"""
        api_url = os.getenv("USER_LIST_URL")
        users =  fetch_data(self, api_url, self.token)
        if users:
            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
                self.user_table.setItem(row, 1, QTableWidgetItem(user["full_name"]))
                self.user_table.setItem(row, 2, QTableWidgetItem(user["role"]))
                self.user_table.setItem(row, 3, QTableWidgetItem(str(user["is_active"])))

                if self.role == "admin":
                    delete_button = QPushButton("Delete")
                    delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
                    delete_button.clicked.connect(lambda _, u_id=user["id"]: self.delete_user(u_id))
                    self.user_table.setCellWidget(row, 4, delete_button)

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
        base_url = os.getenv("USER_LIST_URL")
        api_url = f"{base_url}/{user_id}"
        response = delete_data(self, api_url, self.token)
        if response:
            QMessageBox.information(self, "Success", "User deleted successfully.")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", "Failed to delete user.")
