from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QLineEdit, 
    QHeaderView
)
from PySide6.QtCore import Qt
import requests
import os

class Billing(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        super().__init__()
        self.token = auth_token
        self.role = user_role
        self.user_id = user_id

        # Only specific roles should access billing
        if not auth_token:
            QMessageBox.critical(self, "Access Denied", "You must be logged in to access billing.")
            self.close()
            return
        
        if user_role not in ["admin", "billing", "pharmacist"]:
            QMessageBox.critical(self, "Access Denied", "You do not have permission to access billing.")
            self.close()
            return

        self.init_ui()
        self.load_bills()

    def init_ui(self):
        self.setWindowTitle("Billing Management")
        self.setGeometry(300, 300, 800, 500)
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

        self.title_label = QLabel("Billing & Payments")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.billing_table = QTableWidget()
        self.billing_table.setColumnCount(4)
        self.billing_table.setHorizontalHeaderLabels(["Bill ID", "Patient", "Amount", "Status"])
        self.billing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.billing_table)

        if self.user_role in ["admin", "billing"]:
            self.add_billing_section(layout)

        self.refresh_button = QPushButton("Refresh Bills")
        self.refresh_button.clicked.connect(self.load_bills)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

    def add_billing_section(self, layout):
        """Admin and Billing staff can add new bills"""
        form_layout = QHBoxLayout()

        self.patient_input = QLineEdit()
        self.patient_input.setPlaceholderText("Enter patient ID")
        form_layout.addWidget(self.patient_input)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        form_layout.addWidget(self.amount_input)

        self.add_bill_button = QPushButton("Add Bill")
        self.add_bill_button.clicked.connect(self.add_bill)
        form_layout.addWidget(self.add_bill_button)

        layout.addLayout(form_layout)

    def load_bills(self):
        """Fetches billing data from the backend"""
        api_url = os.getenv("BILLING_LIST_URL")
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            bills = response.json()
            self.billing_table.setRowCount(len(bills))
            for row, bill in enumerate(bills):
                self.billing_table.setItem(row, 0, QTableWidgetItem(str(bill["bill_id"])))
                self.billing_table.setItem(row, 1, QTableWidgetItem(bill["patient_name"]))
                self.billing_table.setItem(row, 2, QTableWidgetItem(f"${bill['amount']}"))
                self.billing_table.setItem(row, 3, QTableWidgetItem(bill["status"]))
        else:
            QMessageBox.critical(self, "Error", "Failed to load billing data.")

    def add_bill(self):
        """Handles adding a new bill"""
        patient_id = self.patient_input.text()
        amount = self.amount_input.text()

        if not patient_id or not amount:
            QMessageBox.warning(self, "Input Error", "Please fill out all fields.")
            return

        api_url = os.getenv("ADD_BILL_URL")
        headers = {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        data = {"patient_id": patient_id, "amount": amount}

        response = requests.post(api_url, json=data, headers=headers)

        if response.status_code == 201:
            QMessageBox.information(self, "Success", "Bill added successfully.")
            self.load_bills()
        else:
            QMessageBox.critical(self, "Error", "Failed to add bill.")
