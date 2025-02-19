import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt


class LabTestManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the Lab Test Management interface.

        :param user_role: Role of the logged-in user (doctor/lab_technician/patient)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.auth_token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Laboratory Test Management")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Laboratory Test Requests")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # Lab Test Requests Table
        self.lab_test_table = QTableWidget()
        self.lab_test_table.setColumnCount(5)
        self.lab_test_table.setHorizontalHeaderLabels(["Patient", "Requested By", "Test Type", "Status", "Results"])
        self.lab_test_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.lab_test_table)

        # Lab Test Request Form (Doctor Only)
        if self.user_role == "doctor":
            form_layout = QVBoxLayout()

            self.patient_dropdown = QComboBox()
            self.load_patients()
            form_layout.addWidget(self.patient_dropdown)

            self.test_type_input = QComboBox()
            self.test_type_input.addItems(["Blood Test", "Urine Test", "ECG", "Liver Function Test"])
            form_layout.addWidget(self.test_type_input)

            self.request_button = QPushButton("Request Lab Test")
            self.request_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            self.request_button.clicked.connect(self.request_lab_test)
            form_layout.addWidget(self.request_button)

            layout.addLayout(form_layout)

        # Load Lab Tests Button
        self.load_lab_tests_button = QPushButton("Refresh Lab Test Requests")
        self.load_lab_tests_button.clicked.connect(self.load_lab_test_requests)
        self.load_lab_tests_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        layout.addWidget(self.load_lab_tests_button)

        self.load_lab_test_requests()
        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with patients (for requesting lab tests)."""
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

    def load_lab_test_requests(self):
        """Fetches and displays lab test requests."""
        try:
            api_url = os.getenv("LAB_TEST_REQUESTS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                lab_tests = response.json()
                self.populate_table(lab_tests)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch lab test requests.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, lab_tests):
        """Fills the lab test requests table with data."""
        self.lab_test_table.setRowCount(len(lab_tests))
        for row, request in enumerate(lab_tests):
            self.lab_test_table.setItem(row, 0, QTableWidgetItem(request["patient_name"]))
            self.lab_test_table.setItem(row, 1, QTableWidgetItem(request["requested_by"]))
            self.lab_test_table.setItem(row, 2, QTableWidgetItem(request["test_type"]))
            self.lab_test_table.setItem(row, 3, QTableWidgetItem(request["status"]))
            self.lab_test_table.setItem(row, 4, QTableWidgetItem(request.get("results", "Pending")))

    def request_lab_test(self):
        """Allows a doctor to request a lab test for a patient."""
        if self.user_role != "doctor":
            QMessageBox.warning(self, "Unauthorized", "Only doctors can request lab tests.")
            return

        patient_id = self.patient_dropdown.currentData()
        test_type = self.test_type_input.currentText()

        if not patient_id or not test_type:
            QMessageBox.warning(self, "Validation Error", "Please select a patient and test type.")
            return

        try:
            api_url = os.getenv("REQUEST_LAB_TEST_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "patient_id": patient_id,
                "test_type": test_type,
                "requested_by": self.user_id
            }
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Lab test request submitted successfully.")
                self.load_lab_test_requests()
            else:
                QMessageBox.critical(self, "Error", "Failed to request lab test.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
