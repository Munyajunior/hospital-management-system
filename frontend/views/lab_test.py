import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QLineEdit, QTextEdit
)
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, post_data


class LabTests(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Lab Test Management interface.

        :param user_role: Role of the logged-in user (doctor/lab_staff/patient)
        :param user_id: ID of the logged-in user (for filtering test requests)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Lab Test Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Lab Tests")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Lab Test Requests Table
        self.lab_test_table = QTableWidget()
        self.lab_test_table.setColumnCount(5)
        self.lab_test_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Test Type", "Status", "Additional Notes"])
        layout.addWidget(self.lab_test_table)

        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        layout.addWidget(self.patient_dropdown)

        # Lab Test Input
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Enter lab test type (e.g., Blood Test, MRI Scan)...")
        layout.addWidget(self.test_input)

        # additional notes
        self.additional_input = QTextEdit()
        self.additional_input.setPlaceholderText("Enter Additional notes")
        layout.addWidget(self.additional_input)
        
        # Button to request lab test
        self.request_test_button = QPushButton("Request Lab Test")
        self.request_test_button.clicked.connect(self.request_lab_test)
        layout.addWidget(self.request_test_button)

        self.load_lab_tests()
        self.setLayout(layout)

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

    def load_lab_tests(self):
        """Fetches and displays lab test requests."""
        base_url = os.getenv("LAB_TESTS_URL")
        api_url = f"{base_url}test/{self.user_id}"
        lab_test = fetch_data(self, api_url, self.token)
        if lab_test:
            self.populate_table(lab_test)
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch Lab tests.")
            
    def populate_table(self, lab_tests):
        """Fills the table with lab test data."""
        self.lab_test_table.setRowCount(len(lab_tests))
        for row, lab_test in enumerate(lab_tests):
            self.lab_test_table.setItem(row, 0, QTableWidgetItem(str(lab_test["patient_id"])))
            self.lab_test_table.setItem(row, 1, QTableWidgetItem(str(lab_test["requested_by"])))
            self.lab_test_table.setItem(row, 2, QTableWidgetItem(lab_test["test_type"]))
            self.lab_test_table.setItem(row, 3, QTableWidgetItem(lab_test["status"]))
            #self.lab_test_table.setItem(row, 4, QTableWidgetItem(lab_test["additional_notes"]))

    def request_lab_test(self):
        """Submits a lab test request for a patient."""
        patient_id = self.patient_dropdown.currentData()
        test_type = self.test_input.text().strip()
        additional_notes = self.additional_input.toPlainText().strip() 

        if not patient_id or not test_type:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        api_url = os.getenv("REQUEST_LAB_TEST_URL")
        data = {
            "requested_by": self.user_id,
            "patient_id": patient_id,
            "test_type": test_type,
            "additional_notes": additional_notes
        }
        
        lab_test = post_data(self, api_url, data, self.token)
        if lab_test:
            QMessageBox.information(self, "Success", "Lab test requested successfully!")
            self.load_lab_tests()  # Refresh the table
            self.test_input.clear()
            self.additional_input.clear()
        else:
                QMessageBox.critical(self, "Error", "Failed to request lab test.")
        