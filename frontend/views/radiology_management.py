import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt


class RadiologyManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the Radiology Management interface.

        :param user_role: Role of the logged-in user (doctor/radiologist/patient)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.auth_token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Radiology & Scan Requests")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Radiology & Scan Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # Scan Requests Table
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(5)
        self.scan_table.setHorizontalHeaderLabels(["Patient", "Requested By", "Scan Type", "Status", "Results"])
        self.scan_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.scan_table)

        # Radiology Request Form (Doctor Only)
        if self.user_role == "doctor":
            form_layout = QVBoxLayout()

            self.patient_dropdown = QComboBox()
            self.load_patients()
            form_layout.addWidget(self.patient_dropdown)

            self.scan_type_input = QComboBox()
            self.scan_type_input.addItems(["MRI", "CT Scan", "X-ray", "Ultrasound"])
            form_layout.addWidget(self.scan_type_input)

            self.request_button = QPushButton("Request Scan")
            self.request_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            self.request_button.clicked.connect(self.request_scan)
            form_layout.addWidget(self.request_button)

            layout.addLayout(form_layout)

        # Load Scan Requests Button
        self.load_scans_button = QPushButton("Refresh Scan Requests")
        self.load_scans_button.clicked.connect(self.load_scan_requests)
        self.load_scans_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        layout.addWidget(self.load_scans_button)

        self.load_scan_requests()
        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with patients (for requesting scans)."""
        if self.user_role != "doctor":
            return

        try:
            api_url = os.getenv("DOCTOR_ASSIGNED_PATIENTS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                patients = response.json()
                for patient in patients:
                    self.patient_dropdown.addItem(patient["name"], patient["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch patient list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def load_scan_requests(self):
        """Fetches and displays scan requests."""
        try:
            api_url = os.getenv("SCAN_REQUESTS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                scan_requests = response.json()
                self.populate_table(scan_requests)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch scan requests.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, scan_requests):
        """Fills the scan requests table with data."""
        self.scan_table.setRowCount(len(scan_requests))
        for row, request in enumerate(scan_requests):
            self.scan_table.setItem(row, 0, QTableWidgetItem(request["patient_name"]))
            self.scan_table.setItem(row, 1, QTableWidgetItem(request["requested_by"]))
            self.scan_table.setItem(row, 2, QTableWidgetItem(request["scan_type"]))
            self.scan_table.setItem(row, 3, QTableWidgetItem(request["status"]))
            self.scan_table.setItem(row, 4, QTableWidgetItem(request.get("results", "Pending")))

    def request_scan(self):
        """Allows a doctor to request a scan for a patient."""
        if self.user_role != "doctor":
            QMessageBox.warning(self, "Unauthorized", "Only doctors can request scans.")
            return

        patient_id = self.patient_dropdown.currentData()
        scan_type = self.scan_type_input.currentText()

        if not patient_id or not scan_type:
            QMessageBox.warning(self, "Validation Error", "Please select a patient and scan type.")
            return

        try:
            api_url = os.getenv("REQUEST_SCAN_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "patient_id": patient_id,
                "scan_type": scan_type,
                "requested_by": self.user_id
            }
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Scan request submitted successfully.")
                self.load_scan_requests()
            else:
                QMessageBox.critical(self, "Error", "Failed to request scan.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
