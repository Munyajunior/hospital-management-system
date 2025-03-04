import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout, QHeaderView, QScrollArea
)
from utils.api_utils import fetch_data, post_data
from PySide6.QtCore import Qt


class Prescriptions(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Prescription Management interface.

        :param user_role: Role of the logged-in user (doctor/nurse/pharmacist)
        :param user_id: ID of the logged-in user (for filtering prescriptions)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Prescription Management")
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdcdc;
                font-size: 14px;
                alternate-background-color: #f9f9f9;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e6fa7;
            }
            QComboBox, QTextEdit {
                background-color: white;
                border: 1px solid #dcdcdc;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Manage Prescriptions")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Scrollable Prescription Table
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(5)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Medication", "Dosage", "Instructions"])
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prescription_table.setAlternatingRowColors(True)
        self.scroll_area.setWidget(self.prescription_table)
        layout.addWidget(self.scroll_area)

        # Patient Selection
        self.patient_dropdown = QComboBox()
        self.patient_dropdown.setPlaceholderText("Select a Patient")
        self.load_patients()
        layout.addWidget(self.patient_dropdown)

        # Input Fields
        self.medication_input = QTextEdit()
        self.medication_input.setPlaceholderText("Enter medication name(s)...")
        layout.addWidget(self.medication_input)

        self.dosage_input = QTextEdit()
        self.dosage_input.setPlaceholderText("Enter dosage...")
        layout.addWidget(self.dosage_input)

        self.instructions_input = QTextEdit()
        self.instructions_input.setPlaceholderText("Enter instructions...")
        layout.addWidget(self.instructions_input)

        # Button Layout
        button_layout = QHBoxLayout()
        self.prescribe_button = QPushButton("Prescribe Medication")
        self.prescribe_button.clicked.connect(self.prescribe_medication)
        button_layout.addWidget(self.prescribe_button)

        layout.addLayout(button_layout)

        # Load existing prescriptions
        self.load_prescriptions()

        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with assigned patients."""
        base_url = os.getenv("ASSIGNED_PATIENTS_URL")
        api_url = f"{base_url}/{self.user_id}/patients"
        patients = fetch_data(self, api_url, self.token)
        
        if not patients:
            QMessageBox.information(self, "No Patients", "No patients have been assigned yet.")
            return
        
        for patient in patients:
            self.patient_dropdown.addItem(patient["full_name"], patient["id"])

    def load_prescriptions(self):
        """Fetches and displays prescriptions."""
        api_url = os.getenv("PRESCRIPTIONS_URL")
        prescriptions = fetch_data(self, api_url, self.token)
        if not prescriptions:
            QMessageBox.information(self, "No Prescriptions", "No prescriptions available yet.")
            return
        self.populate_table(prescriptions)

    def populate_table(self, prescriptions):
        """Fills the table with prescription data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(prescription["patient_id"]))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(prescription["prescribed_by"]))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["drug_name"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["dosage"]))
            self.prescription_table.setItem(row, 4, QTableWidgetItem(prescription["instructions"]))

    def prescribe_medication(self):
        """Prescribes new medication to a patient."""
        patient_id = self.patient_dropdown.currentData()
        medication = self.medication_input.toPlainText().strip()
        instructions = self.instructions_input.toPlainText().strip()
        dosage = self.dosage_input.toPlainText().strip()

        if not patient_id or not medication or not instructions or not dosage:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        api_url = os.getenv("PRESCRIPTIONS_URL")
        data = {
            "prescribed_by": self.user_id,
            "patient_id": patient_id,
            "drug_name": medication,
            "dosage": dosage,
            "instructions": instructions,
        }

        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Medication prescribed successfully!")
            self.load_prescriptions()  # Refresh the table
            self.medication_input.clear()
            self.instructions_input.clear()
            self.dosage_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to prescribe medication.")
