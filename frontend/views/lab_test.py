import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt


class LabTests(QWidget):
    def __init__(self, user_role, user_id):
        """
        Initializes the Lab Test Management interface.

        :param user_role: Role of the logged-in user (doctor/lab_staff/patient)
        :param user_id: ID of the logged-in user (for filtering test requests)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Lab Test Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Lab Tests")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Lab Test Requests Table
        self.lab_test_table = QTableWidget()
        self.lab_test_table.setColumnCount(4)
        self.lab_test_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Test Type", "Status"])
        layout.addWidget(self.lab_test_table)

        if self.user_role == "doctor":
            # Dropdown to select a patient
            self.patient_dropdown = QComboBox()
            self.load_patients()
            layout.addWidget(self.patient_dropdown)

            # Lab Test Input
            self.test_input = QTextEdit()
            self.test_input.setPlaceholderText("Enter lab test type (e.g., Blood Test, MRI Scan)...")
            layout.addWidget(self.test_input)

            # Button to request lab test
            self.request_test_button = QPushButton("Request Lab Test")
            self.request_test_button.clicked.connect(self.request_lab_test)
            layout.addWidget(self.request_test_button)

        self.load_lab_tests()
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

    def load_lab_tests(self):
        """Fetches and displays lab test requests."""
        try:
            api_url = os.getenv("LAB_TESTS_URL")
            response = requests.get(f"{api_url}?user_id={self.user_id}&role={self.user_role}")
            if response.status_code == 200:
                lab_tests = response.json()
                self.populate_table(lab_tests)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch lab test requests.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, lab_tests):
        """Fills the table with lab test data."""
        self.lab_test_table.setRowCount(len(lab_tests))
        for row, lab_test in enumerate(lab_tests):
            self.lab_test_table.setItem(row, 0, QTableWidgetItem(lab_test["patient_name"]))
            self.lab_test_table.setItem(row, 1, QTableWidgetItem(lab_test["doctor_name"]))
            self.lab_test_table.setItem(row, 2, QTableWidgetItem(lab_test["test_type"]))
            self.lab_test_table.setItem(row, 3, QTableWidgetItem(lab_test["status"]))

    def request_lab_test(self):
        """Submits a lab test request for a patient."""
        patient_id = self.patient_dropdown.currentData()
        test_type = self.test_input.toPlainText().strip()

        if not patient_id or not test_type:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        try:
            api_url = os.getenv("REQUEST_LAB_TEST_URL")
            data = {
                "doctor_id": self.user_id,
                "patient_id": patient_id,
                "test_type": test_type,
            }
            response = requests.post(api_url, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Lab test requested successfully!")
                self.load_lab_tests()  # Refresh the table
                self.test_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to request lab test.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
