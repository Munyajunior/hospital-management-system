from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QComboBox, 
    QLineEdit, QHeaderView
)
from PySide6.QtCore import Qt
import requests
import os

class UserManagement(QWidget):
    def __init__(self, auth_token, user_role):
        super().__init__()
        self.auth_token = auth_token
        self.user_role = user_role

        # Enforce authentication
        if not auth_token:
            QMessageBox.critical(self, "Access Denied", "You must be logged in to access this page.")
            self.close()
            return
        
        if user_role not in ["admin", "nurse", "doctor", "pharmacist"]:
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
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Name", "Role", "Actions"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)

        if self.user_role == "admin":  
            self.add_user_section(layout)

        self.refresh_button = QPushButton("Refresh Users")
        self.refresh_button.clicked.connect(self.load_users)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def add_user_section(self, layout):
        """Admin-only section for adding new users."""
        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name")
        form_layout.addWidget(self.name_input)

        self.role_select = QComboBox()
        self.role_select.addItems(["doctor", "nurse", "pharmacist", "lab_technician", "radiologist", "admin"])
        form_layout.addWidget(self.role_select)

        self.add_user_button = QPushButton("Add User")
        self.add_user_button.clicked.connect(self.add_user)
        form_layout.addWidget(self.add_user_button)

        layout.addLayout(form_layout)

    def load_users(self):
        """Fetches user data from the backend API"""
        api_url = os.getenv("USER_LIST_URL")
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            users = response.json()
            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user["user_id"])))
                self.user_table.setItem(row, 1, QTableWidgetItem(user["name"]))
                self.user_table.setItem(row, 2, QTableWidgetItem(user["role"]))

                if self.user_role == "admin":
                    delete_button = QPushButton("Delete")
                    delete_button.setStyleSheet("background-color: red; color: white; border-radius: 5px;")
                    delete_button.clicked.connect(lambda _, u_id=user["user_id"]: self.delete_user(u_id))
                    self.user_table.setCellWidget(row, 3, delete_button)

        else:
            QMessageBox.critical(self, "Error", "Failed to load user data.")

    def add_user(self):
        """Handles adding a new user (Admin only)."""
        name = self.name_input.text()
        role = self.role_select.currentText()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter a name.")
            return

        api_url = os.getenv("ADD_USER_URL")
        headers = {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        data = {"name": name, "role": role}
        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 201:
            QMessageBox.information(self, "Success", "User added successfully.")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", "Failed to add user.")

    def delete_user(self, user_id):
        """Handles user deletion (Admin only)."""
        api_url = os.getenv("DELETE_USER_URL") + f"/{user_id}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.delete(api_url, headers=headers)

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "User deleted successfully.")
            self.load_users()
        else:
            QMessageBox.critical(self, "Error", "Failed to delete user.")
