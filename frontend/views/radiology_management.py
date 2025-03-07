import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, post_data,update_data


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
        self.token = auth_token
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

        

        # Load Scan Requests Button
        self.load_scans_button = QPushButton("Update Scan Results")
        self.load_scans_button.clicked.connect(self.load_scan_requests)
        self.load_scans_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        layout.addWidget(self.load_scans_button)

        self.load_scan_requests()
        self.setLayout(layout)


    def load_scan_requests(self):
        """Fetches and displays scan requests."""
        api_url = os.getenv("SCAN_URL")
        requests = fetch_data(self, api_url, self.token)
        if not requests:
            QMessageBox.information(self, "No requests", "No Scan requests have been sent made.")
            return
        self.populate_table(requests)
            

    def populate_table(self, scan_requests):
        """Fills the scan requests table with data."""
        self.scan_table.setRowCount(len(scan_requests))
        for row, request in enumerate(scan_requests):
            self.scan_table.setItem(row, 0, QTableWidgetItem(request["patient_id"]))
            self.scan_table.setItem(row, 1, QTableWidgetItem(request["requested_by"]))
            self.scan_table.setItem(row, 2, QTableWidgetItem(request["scan_type"]))
            self.scan_table.setItem(row, 3, QTableWidgetItem(request["status"]))
            self.scan_table.setItem(row, 4, QTableWidgetItem(request.get("results", "Pending")))
            self.scan_table.setItem(row, 4, QTableWidgetItem(request["additional_notes"]))

    def request_scan(self):
        """Update status to In-Progress when the request have being processed"""
        base_url = os.getenv("SCANS_URL")
        