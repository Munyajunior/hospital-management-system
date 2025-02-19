import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt


class Scans(QWidget):
    def __init__(self, user_role, user_id):
        """
        Initializes the Scan Management interface.

        :param user_role: Role of the logged-in user (doctor/radiology_staff/patient)
        :param user_id: ID of the logged-in user (for filtering scan requests)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Scan Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Scans")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Scan Requests Table
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(4)
        self.scan_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Scan Type", "Status"])
        layout.addWidget(self.scan_table)

        if self.user_role == "doctor":
            # Dropdown to select a patient
            self.patient_dropdown = QComboBox()
            self.load_patients()
            layout.addWidget(self.patient_dropdown)

            # Scan Type Input
            self.scan_input = QTextEdit()
            self.scan_input.setPlaceholderText("Enter scan type (e.g., X-Ray, MRI, CT Scan)...")
            layout.addWidget(self.scan_input)

            # Button to request scan
            self.request_scan_button = QPushButton("Request Scan")
            self.request_scan_button.clicked.connect(self.request_scan)
            layout.addWidget(self.request_scan_button)

        self.load_scans()
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

    def load_scans(self):
        """Fetches and displays scan requests."""
        try:
            api_url = os.getenv("SCANS_URL")
            response = requests.get(f"{api_url}?user_id={self.user_id}&role={self.user_role}")
            if response.status_code == 200:
                scans = response.json()
                self.populate_table(scans)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch scan requests.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, scans):
        """Fills the table with scan data."""
        self.scan_table.setRowCount(len(scans))
        for row, scan in enumerate(scans):
            self.scan_table.setItem(row, 0, QTableWidgetItem(scan["patient_name"]))
            self.scan_table.setItem(row, 1, QTableWidgetItem(scan["doctor_name"]))
            self.scan_table.setItem(row, 2, QTableWidgetItem(scan["scan_type"]))
            self.scan_table.setItem(row, 3, QTableWidgetItem(scan["status"]))

    def request_scan(self):
        """Submits a scan request for a patient."""
        patient_id = self.patient_dropdown.currentData()
        scan_type = self.scan_input.toPlainText().strip()

        if not patient_id or not scan_type:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return
