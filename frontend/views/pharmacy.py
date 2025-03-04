import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
from utils.api_utils import fetch_data, post_data, update_data
from PySide6.QtCore import Qt


class Pharmacy(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Pharmacy Management interface.

        :param user_role: Role of the logged-in user (doctor/pharmacist/patient)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pharmacy Management")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Pharmacy & Medication Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # Prescription Requests Table
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(7)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Medication", "Dosage", "Instructions", "Status", "Action"])
        self.prescription_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.prescription_table)

        # Pharmacist UI: Manage Inventory
        if self.user_role == "pharmacist":
            self.load_inventory_button = QPushButton("Load Inventory")
            self.load_inventory_button.clicked.connect(self.load_inventory)
            self.load_inventory_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
            layout.addWidget(self.load_inventory_button)

            self.inventory_table = QTableWidget()
            self.inventory_table.setColumnCount(3)
            self.inventory_table.setHorizontalHeaderLabels(["Medication", "Quantity", "Availability"])
            self.inventory_table.setStyleSheet("QTableWidget { font-size: 14px; }")
            layout.addWidget(self.inventory_table)

        self.load_prescriptions()
        self.setLayout(layout)

    

    def load_prescriptions(self):
        """Fetches and displays prescription requests based on user role."""
        
        api_url = os.getenv("PRESCRIPTIONS_URL")
        prescriptions = fetch_data(self, api_url, self.token)
        
        if not prescriptions:
            QMessageBox.information(self, "No PRESCRIPTIONS", "No Drugs prescribed at the moment")
            return
        
        self.populate_table(prescriptions)
        

    def populate_table(self, prescriptions):
        """Fills the prescription table with data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(prescription["patient_id"]))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(prescription["prescribed_by"]))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["drug_name"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["dosage"]))
            self.prescription_table.setItem(row, 4, QTableWidgetItem(prescription["instructions"]))
            self.prescription_table.setItem(row, 5, QTableWidgetItem(prescription["status"]))

            self.prescription_table.setCellWidget(row, 6, self.dispense_drug(prescription["id"]))
            
            

    def load_inventory(self):
        """Fetches and displays pharmacy inventory (pharmacist only)."""
        if self.user_role != "pharmacist":
            QMessageBox.warning(self, "Unauthorized", "Only pharmacists can view the inventory.")
            return

        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory =  fetch_data(self, api_url, self.token)
        if not inventory:
            QMessageBox.information(self, "No inventory", "Please Add inventory")
            return
        self.populate_inventory_table(inventory)
        

    def populate_inventory_table(self, inventory):
        """Fills the inventory table with data."""
        self.inventory_table.setRowCount(len(inventory))
        for row, item in enumerate(inventory):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item["drug_name"]))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
            availability = "In Stock" if item["quantity"] > 0 else "Out of Stock"
            self.inventory_table.setItem(row, 2, QTableWidgetItem(availability))

    def dispense_drug(self, prescription_id):
        QMessageBox.information(self, "Dispense Drug", "NOT IMPLEMENTED, COMING SOON...")