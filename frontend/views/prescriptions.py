import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt

class PrescriptionManagement(QWidget):
    def __init__(self, doctor_id):
        super().__init__()
        self.doctor_id = doctor_id
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
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Medications", "Lab Tests", "Scans"])
        layout.addWidget(self.prescription_table)

        # Buttons for actions
        self.refresh_button = QPushButton("Refresh Prescriptions")
        self.refresh_button.clicked.connect(self.load_prescriptions)
        layout.addWidget(self.refresh_button)

        self.prescribe_button = QPushButton("Prescribe Medication / Tests / Scans")
        self.prescribe_button.clicked.connect(self.show_prescribe_form)
        layout.addWidget(self.prescribe_button)

        self.setLayout(layout)

        self.load_prescriptions()

    def load_prescriptions(self):
        """Fetch prescription data from API"""
        try:
            api_url = os.getenv("PRESCRIPTION_LIST_URL")
            response = requests.get(f"{api_url}?doctor_id={self.doctor_id}")
            if response.status_code == 200:
                prescriptions = response.json()
                self.populate_table(prescriptions)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch prescription data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, prescriptions):
        """Populate table with prescription data"""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(prescription["patient_name"]))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(", ".join(prescription["medications"])))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(", ".join(prescription["lab_tests"])))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(", ".join(prescription["scans"])))

    def show_prescribe_form(self):
        """Show prescription form for the doctor"""
        self.prescribe_window = PrescriptionForm(self)
        self.prescribe_window.show()


class PrescriptionForm(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Prescribe Medication & Tests")

        layout = QVBoxLayout()

        self.patient_input = QComboBox()
        self.load_patients()
        layout.addWidget(self.patient_input)

        self.medications_input = QTextEdit()
        self.medications_input.setPlaceholderText("Enter prescribed medications (comma-separated)")
        layout.addWidget(self.medications_input)

        self.lab_tests_input = QTextEdit()
        self.lab_tests_input.setPlaceholderText("Enter lab tests (comma-separated)")
        layout.addWidget(self.lab_tests_input)

        self.scans_input = QTextEdit()
        self.scans_input.setPlaceholderText("Enter scan types (comma-separated)")
        layout.addWidget(self.scans_input)

        self.submit_button = QPushButton("Submit Prescription")
        self.submit_button.clicked.connect(self.submit_prescription)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def load_patients(self):
        """Fetch assigned patients for the doctor"""
        try:
            api_url = os.getenv("ASSIGNED_PATIENTS_URL")
            response = requests.get(f"{api_url}?doctor_id={self.parent.doctor_id}")
            if response.status_code == 200:
                patients = response.json()
                for patient in patients:
                    self.patient_input.addItem(patient["name"], patient["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch patients.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def submit_prescription(self):
        """Submit prescription data to API"""
        patient_id = self.patient_input.currentData()
        medications = [med.strip() for med in self.medications_input.toPlainText().split(",") if med.strip()]
        lab_tests = [test.strip() for test in self.lab_tests_input.toPlainText().split(",") if test.strip()]
        scans = [scan.strip() for scan in self.scans_input.toPlainText().split(",") if scan.strip()]

        if not patient_id or not (medications or lab_tests or scans):
            QMessageBox.warning(self, "Validation Error", "Please enter at least one medication, lab test, or scan!")
            return

        try:
            api_url = os.getenv("SUBMIT_PRESCRIPTION_URL")
            data = {
                "doctor_id": self.parent.doctor_id,
                "patient_id": patient_id,
                "medications": medications,
                "lab_tests": lab_tests,
                "scans": scans
            }
            response = requests.post(api_url, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Prescription submitted successfully!")
                self.parent.load_prescriptions()
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to submit prescription.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
