import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QHBoxLayout, QHeaderView
)
from utils.api_utils import fetch_data, post_data, update_data
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator


class Pharmacy(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Pharmacy Management interface.

        :param user_role: Role of the logged-in user (doctor/pharmacy/patient)
        :param user_id: ID of the logged-in user
        :param token: Authentication token for API authorization
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
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prescription_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.prescription_table)

        # Pharmacist UI: Manage Inventory
        if self.user_role == "pharmacy":
            self.load_inventory_button = QPushButton("Load Inventory")
            self.load_inventory_button.clicked.connect(self.load_inventory)
            self.load_inventory_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
            layout.addWidget(self.load_inventory_button)

            self.inventory_table = QTableWidget()
            self.inventory_table.setColumnCount(3)
            self.inventory_table.setHorizontalHeaderLabels(["Medication", "Quantity", "Availability"])
            self.inventory_table.setStyleSheet("QTableWidget { font-size: 14px; }")
            layout.addWidget(self.inventory_table)
            
            
            # Inputs for Adding New Inventory
            inventory_form_layout = QHBoxLayout()
            self.drug_name_input = QLineEdit()
            self.drug_name_input.setPlaceholderText("Enter drug name")
            self.quantity_input = QLineEdit()
            self.quantity_input.setPlaceholderText("Enter quantity")
            self.quantity_input.setValidator(QIntValidator(0, 1000000))  # Restrict input to numbers

            self.add_inventory_button = QPushButton("Add to Inventory")
            self.add_inventory_button.setStyleSheet("background-color: #28a745; color: white; padding: 8px;")
            self.add_inventory_button.clicked.connect(self.add_to_inventory)

            inventory_form_layout.addWidget(self.drug_name_input)
            inventory_form_layout.addWidget(self.quantity_input)
            inventory_form_layout.addWidget(self.add_inventory_button)
            layout.addLayout(inventory_form_layout)

        self.load_prescriptions()
        self.setLayout(layout)

    def load_prescriptions(self):
        """Fetches and displays prescription requests based on user role."""
        
        api_url = os.getenv("PRESCRIPTIONS_URL")
        prescriptions = fetch_data(self, api_url, self.token)
        
        if not prescriptions:
            QMessageBox.information(self, "No Prescriptions", "No drugs prescribed at the moment")
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

            # Create a button for dispensing medication
            dispense_button = QPushButton("Dispense")
            dispense_button.setStyleSheet("background-color: #28a745; color: white; padding: 5px;")
            dispense_button.clicked.connect(lambda _, pid=prescription["id"], drug=prescription["drug_name"]: self.dispense_prescription(pid, drug))
            self.prescription_table.setCellWidget(row, 6, dispense_button)

    def load_inventory(self):
        """Fetches and displays pharmacy inventory (pharmacist only)."""
        if self.user_role != "pharmacy":
            QMessageBox.warning(self, "Unauthorized", "Only pharmacists can view the inventory.")
            return

        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory = fetch_data(self, api_url, self.token)
        if not inventory:
            QMessageBox.information(self, "No Inventory", "Please add inventory")
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

    def dispense_prescription(self, prescription_id, drug_name):
        """Dispenses medication and updates stock and prescription status."""
        
        # Check inventory for the prescribed drug
        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory = fetch_data(self, api_url, self.token)
        if not inventory:
            QMessageBox.warning(self, "Inventory Error", "No inventory records found.")
            return
        
        # Find the drug in inventory
        drug_item = next((item for item in inventory if item["drug_name"].lower() == drug_name.lower()), None)

        if not drug_item:
            QMessageBox.warning(self, "Stock Error", f"'{drug_name}' is not available in inventory.")
            return

        if drug_item["quantity"] <= 0:
            QMessageBox.critical(self, "Out of Stock", f"'{drug_name}' is out of stock. Cannot dispense.")
            return

        # Reduce inventory count
        new_quantity = drug_item["quantity"] - 1

        # Update Inventory 
        update_url = f"{api_url}/{drug_item['id']}"
        inventory_update_data = {"quantity": new_quantity}
        inventory_updated = update_data(self, update_url, inventory_update_data, self.token)

        if not inventory_updated:
            QMessageBox.critical(self, "Update Error", "Failed to update inventory. Please try again.")
            return

        # Update Prescription Status to "Dispensed"
        prescription_update_url = f"{os.getenv('PRESCRIPTIONS_URL')}/{prescription_id}/dispense"
        prescription_update_data = {"status": "Dispensed"}
        prescription_updated = update_data(self, prescription_update_url, prescription_update_data, self.token)

        if prescription_updated:
            QMessageBox.information(self, "Success", f"'{drug_name}' has been dispensed successfully!")
            self.load_prescriptions()  # Refresh the table
            self.load_inventory()  # Refresh inventory
        else:
            QMessageBox.critical(self, "Error", "Failed to update prescription status.")

    def add_to_inventory(self):
        """Adds a new drug to the inventory."""
        drug_name = self.drug_name_input.text().strip()
        quantity = self.quantity_input.text().strip()
        added_by =  self.user_id

        if not drug_name or not quantity or not added_by:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        data = {"drug_name": drug_name, "quantity": int(quantity), "added_by": int(added_by)}
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Drug added to inventory!")
            self.load_inventory()
            self.drug_name_input.clear()
            self.quantity_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to add drug.")