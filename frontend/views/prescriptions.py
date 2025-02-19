import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt


class Prescriptions(QWidget):
    def __init__(self, user_role, user_id):
        """
        Initializes the Prescription Management interface.

        :param user_role: Role of the logged-in user (doctor/nurse/pharmacist)
        :param user_id: ID of the logged-in user (for filtering prescriptions)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Prescription Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Prescriptions")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Prescription Table
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(4)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Medication", "Instructions"])
        layout.addWidget(self.prescription_table)

        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        layout.addWidget(self.patient_dropdown)

        # Medication Input
        self.medication_input = QTextEdit()
        self.medication_input.setPlaceholderText("Enter medication name(s)...")
        layout.addWidget(self.medication_input)

        # Instructions Input
        self.instructions_input = QTextEdit()
        self.instructions_input.setPlaceholderText("Enter dosage instructions...")
        layout.addWidget(self.instructions_input)

        # Button to prescribe medication
        self.prescribe_button = QPushButton("Prescribe Medication")
        self.prescribe_button.clicked.connect(self.prescribe_medication)
        layout.addWidget(self.prescribe_button)

        # Load existing prescriptions
        self.load_prescriptions()

        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with assigned patients."""
        try:
            api_url = os.getenv("ASSIGNED_PATIENTS_URL")
            response = requests.get(f"{api_url}?user_id={self.user_id}&role={self.user_role}")
            if response.status_code == 200:
                patients = response.json()
                for patient in patients:
                    self.patient_dropdown.addItem(patient["name"], patient["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch patient list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def load_prescriptions(self):
        """Fetches and displays prescriptions."""
        try:
            api_url = os.getenv("PRESCRIPTIONS_URL")
            response = requests.get(f"{api_url}?user_id={self.user_id}&role={self.user_role}")
            if response.status_code == 200:
                prescriptions = response.json()
                self.populate_table(prescriptions)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch prescriptions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, prescriptions):
        """Fills the table with prescription data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(prescription["patient_name"]))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(prescription["doctor_name"]))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["medication"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["instructions"]))

    def prescribe_medication(self):
        """Prescribes new medication to a patient."""
        patient_id = self.patient_dropdown.currentData()
        medication = self.medication_input.toPlainText().strip()
        instructions = self.instructions_input.toPlainText().strip()

        if not patient_id or not medication or not instructions:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        try:
            api_url = os.getenv("PRESCRIBE_MEDICATION_URL")
            data = {
                "doctor_id": self.user_id,
                "patient_id": patient_id,
                "medication": medication,
                "instructions": instructions,
            }
            response = requests.post(api_url, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Medication prescribed successfully!")
                self.load_prescriptions()  # Refresh the table
                self.medication_input.clear()
                self.instructions_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to prescribe medication.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
