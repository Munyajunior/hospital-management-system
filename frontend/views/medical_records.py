import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt


class MedicalRecords(QWidget):
    def __init__(self, user_role, user_id):
        """
        Initializes the Medical Records interface.
        
        :param user_role: Role of the logged-in user (doctor/nurse)
        :param user_id: ID of the logged-in user (for role-based filtering)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Medical Records Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Patient Medical Records")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Records Table
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(5)
        self.records_table.setHorizontalHeaderLabels(["Patient", "Diagnoses", "Prescriptions", "Lab Results", "Scans"])
        layout.addWidget(self.records_table)

        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        layout.addWidget(self.patient_dropdown)

        # Button to view selected patient's medical record
        self.view_button = QPushButton("View Medical Record")
        self.view_button.clicked.connect(self.load_medical_record)
        layout.addWidget(self.view_button)

        # Medical Notes Section (For Doctors and Nurses)
        if self.user_role in ["doctor", "nurse"]:
            self.notes_input = QTextEdit()
            self.notes_input.setPlaceholderText("Enter medical notes...")
            layout.addWidget(self.notes_input)

            self.add_note_button = QPushButton("Add Medical Notes")
            self.add_note_button.clicked.connect(self.add_medical_note)
            layout.addWidget(self.add_note_button)

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

    def load_medical_record(self):
        """Fetches and displays the selected patient's medical record."""
        patient_id = self.patient_dropdown.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient!")
            return

        try:
            api_url = os.getenv("MEDICAL_RECORD_URL")
            response = requests.get(f"{api_url}?patient_id={patient_id}")
            if response.status_code == 200:
                record = response.json()
                self.populate_table(record)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch medical records.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, record):
        """Fills the table with medical record data."""
        self.records_table.setRowCount(1)
        self.records_table.setItem(0, 0, QTableWidgetItem(record["patient_name"]))
        self.records_table.setItem(0, 1, QTableWidgetItem("\n".join(record["diagnoses"])))
        self.records_table.setItem(0, 2, QTableWidgetItem("\n".join(record["prescriptions"])))
        self.records_table.setItem(0, 3, QTableWidgetItem("\n".join(record["lab_results"])))
        self.records_table.setItem(0, 4, QTableWidgetItem("\n".join(record["scans"])))

    def add_medical_note(self):
        """Allows doctors and nurses to add notes to a patient's medical record."""
        patient_id = self.patient_dropdown.currentData()
        notes = self.notes_input.toPlainText().strip()

        if not patient_id or not notes:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid medical note.")
            return

        try:
            api_url = os.getenv("ADD_MEDICAL_NOTE_URL")
            data = {"user_id": self.user_id, "patient_id": patient_id, "notes": notes}
            response = requests.post(api_url, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Medical note added successfully!")
                self.notes_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to add medical note.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
