import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt


class Pharmacy(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the Pharmacy Management interface.

        :param user_role: Role of the logged-in user (doctor/pharmacist/patient)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.auth_token = auth_token
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
        self.prescription_table.setColumnCount(4)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Medication", "Status"])
        self.prescription_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.prescription_table)

        # Doctor UI: Prescribe Medication
        if self.user_role == "doctor":
            self.patient_dropdown = QComboBox()
            self.load_patients()
            layout.addWidget(self.patient_dropdown)

            self.medication_input = QTextEdit()
            self.medication_input.setPlaceholderText("Enter prescribed medication (e.g., Paracetamol 500mg)...")
            layout.addWidget(self.medication_input)

            self.request_prescription_button = QPushButton("Prescribe Medication")
            self.request_prescription_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            self.request_prescription_button.clicked.connect(self.request_prescription)
            layout.addWidget(self.request_prescription_button)

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

    def load_patients(self):
        """Fetches and populates the dropdown with assigned patients."""
        if self.user_role != "doctor":
            return

        try:
            api_url = os.getenv("ASSIGNED_PATIENTS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{api_url}?user_id={self.user_id}", headers=headers)

            if response.status_code == 200:
                patients = response.json()
                for patient in patients:
                    self.patient_dropdown.addItem(patient["name"], patient["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch patient list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def load_prescriptions(self):
        """Fetches and displays prescription requests based on user role."""
        try:
            api_url = os.getenv("PRESCRIPTIONS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{api_url}?user_id={self.user_id}&role={self.user_role}", headers=headers)

            if response.status_code == 200:
                prescriptions = response.json()
                self.populate_table(prescriptions)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch prescription requests.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, prescriptions):
        """Fills the prescription table with data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(prescription["patient_name"]))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(prescription["doctor_name"]))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["medication"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["status"]))

    def request_prescription(self):
        """Submits a prescription request (doctor only)."""
        if self.user_role != "doctor":
            QMessageBox.warning(self, "Unauthorized", "Only doctors can prescribe medication.")
            return

        patient_id = self.patient_dropdown.currentData()
        medication = self.medication_input.toPlainText().strip()

        if not patient_id or not medication:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        try:
            api_url = os.getenv("REQUEST_PRESCRIPTION_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "doctor_id": self.user_id,
                "patient_id": patient_id,
                "medication": medication,
            }
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Medication prescribed successfully!")
                self.load_prescriptions()
                self.medication_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to request prescription.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def load_inventory(self):
        """Fetches and displays pharmacy inventory (pharmacist only)."""
        if self.user_role != "pharmacist":
            QMessageBox.warning(self, "Unauthorized", "Only pharmacists can view the inventory.")
            return

        try:
            api_url = os.getenv("PHARMACY_INVENTORY_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                inventory = response.json()
                self.populate_inventory_table(inventory)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch inventory.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_inventory_table(self, inventory):
        """Fills the inventory table with data."""
        self.inventory_table.setRowCount(len(inventory))
        for row, item in enumerate(inventory):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item["medication"]))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
            availability = "In Stock" if item["quantity"] > 0 else "Out of Stock"
            self.inventory_table.setItem(row, 2, QTableWidgetItem(availability))
