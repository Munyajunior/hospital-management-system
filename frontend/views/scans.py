import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QLineEdit, QFormLayout, QHeaderView
)
from utils.api_utils import fetch_data, post_data
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon


class Scans(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Scan Management interface.

        :param user_role: Role of the logged-in user (doctor/radiology_staff/patient)
        :param user_id: ID of the logged-in user (for filtering scan requests)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        if self.user_role in ["doctor","admin"]:
            self.setWindowTitle("Scan Request")
            self.setMinimumSize(900, 600)
            self.init_ui()
        else:
            QMessageBox.warning(self,"Unauthorized access", "You are not authorized to access this interface")

    def init_ui(self):
        self.setStyleSheet("""
                           QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
                QComboBox, QLineEdit {
                background-color: white;
                border: 1px solid #dcdcdc;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }""")

        layout = QVBoxLayout()
        self.title_label = QLabel("Manage Scans")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # Scan Requests Table
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(6)
        self.scan_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Scan Type", "Status","Results", "Additional Notes"])
        self.scan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scan_table.setAlternatingRowColors(True)
        self.scan_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                gridline-color: #ddd;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(self.scan_table)

        form_layout = QFormLayout()
        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        form_layout.addRow("Patient ID",self.patient_dropdown)

        # Scan Type Input
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Enter scan type (e.g., X-Ray, MRI, CT Scan)...")
        form_layout.addRow("Scan Type", self.scan_input)
        
        layout.addLayout(form_layout)

        # Button to request scan
        self.request_scan_button = QPushButton("Request Scan")
        self.request_scan_button.setIcon(QIcon("assets/icons/add.png"))
        self.request_scan_button.clicked.connect(self.request_scan)
        self.request_scan_button.setStyleSheet(self.button_style())
        layout.addWidget(self.request_scan_button)
        
        self.load_scans_button = QPushButton("Refresh Scan Requests")
        self.load_scans_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.load_scans_button.clicked.connect(self.load_scan_requests)
        self.load_scans_button.setStyleSheet(self.button_style())
        layout.addWidget(self.load_scans_button)

        self.load_scan_requests()
        self.setLayout(layout)



    @staticmethod
    def button_style():
        """Return CSS for the submit button."""
        return """
            QPushButton {
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #007BFF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

    def load_patients(self):
        """Fetches and populates the dropdown with assigned patients."""
        base_url = os.getenv("ASSIGNED_PATIENTS_URL")
        api_url = f"{base_url}/{self.user_id}/patients"
        patients = fetch_data(self, api_url, self.token)
        if patients:
            for patient in patients:
                self.patient_dropdown.addItem(patient["full_name"], patient["id"])
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch patients.")
        

    def load_scan_requests(self):
        """Fetches and displays scan requests."""
        base_url =  os.getenv("SCANS_URL")
        api_url =f"{base_url}scan/{self.user_id}"
        patients_scan = fetch_data(self, api_url, self.token)
        if not patients_scan:
            QMessageBox.information(self, "No patients", "No patients Scans were found")
            return
        self.populate_table(patients_scan)
        
   

    def populate_table(self, scans):
        """Fills the table with scan data."""
        self.scan_table.setRowCount(len(scans))
        for row, scan in enumerate(scans):
            self.scan_table.setItem(row, 0, QTableWidgetItem(str(scan["patient_id"])))
            self.scan_table.setItem(row, 1, QTableWidgetItem(str(scan["requested_by"])))
            self.scan_table.setItem(row, 2, QTableWidgetItem(scan["scan_type"]))
            self.scan_table.setItem(row, 3, QTableWidgetItem(scan["status"]))
            if scan["status"] == "Completed":
                self.scan_table.setItem(row, 4, QTableWidgetItem(scan["results"]))
                self.scan_table.setItem(row, 5, QTableWidgetItem(scan["additional_notes"]))
                
                

    def request_scan(self):
        """Submits a scan request for a patient."""
        patient_id = int(self.patient_dropdown.currentData())
        scan_type = self.scan_input.text().strip()
        requested_by = int(self.user_id)
        
        
        if not patient_id or not scan_type:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return
        data = {
            "patient_id": patient_id,
            "scan_type" : scan_type,
            "requested_by" : requested_by
        }
        api_url = os.getenv("SCANS_URL")
        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Operation Successful", "Scan Requested Successfully")
            self.load_scan_requests()
        else:
            QMessageBox.warning(self, "Operation Failed", "Scan Request Failed")