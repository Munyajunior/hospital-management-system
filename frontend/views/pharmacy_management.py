import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHeaderView, QApplication
)
from PySide6.QtCore import Qt


class PharmacyManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the Pharmacy Management interface.

        :param user_role: Role of the logged-in user (pharmacist/doctor/patient)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.auth_token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pharmacy Management")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(900, 600)  # Set a reasonable minimum size

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Pharmacy & Prescriptions")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # Prescription Table
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(5)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Prescribed By", "Medication", "Dosage", "Status"])
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prescription_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.prescription_table)

        # Prescription Approval (Pharmacist Only)
        if self.user_role == "pharmacist":
            self.approve_button = QPushButton("Approve Selected Prescription")
            self.approve_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            self.approve_button.clicked.connect(self.approve_prescription)
            layout.addWidget(self.approve_button)

        # Prescription Request Form (Doctor Only)
        if self.user_role == "doctor":
            form_layout = QVBoxLayout()

            self.patient_dropdown = QComboBox()
            self.load_patients()
            form_layout.addWidget(self.patient_dropdown)

            self.medication_input = QTextEdit()
            self.medication_input.setPlaceholderText("Enter medication details...")
            form_layout.addWidget(self.medication_input)

            self.prescribe_button = QPushButton("Prescribe Medication")
            self.prescribe_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
            self.prescribe_button.clicked.connect(self.prescribe_medication)
            form_layout.addWidget(self.prescribe_button)

            layout.addLayout(form_layout)

        # Load Prescriptions Button
        self.load_prescriptions_button = QPushButton("Refresh Prescriptions")
        self.load_prescriptions_button.clicked.connect(self.load_prescriptions)
        self.load_prescriptions_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        layout.addWidget(self.load_prescriptions_button)

        self.load_prescriptions()
        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with patients (for prescribing medication)."""
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

    def load_prescriptions(self):
        """Fetches and displays prescriptions."""
        try:
            api_url = os.getenv("PRESCRIPTIONS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                prescriptions = response.json()
                self.populate_table(prescriptions)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch prescriptions.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, prescriptions):
        """Fills the prescription table with data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(prescription["patient_name"]))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(prescription["prescribed_by"]))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["medication"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["dosage"]))
            self.prescription_table.setItem(row, 4, QTableWidgetItem(prescription["status"]))

    def prescribe_medication(self):
        """Allows a doctor to prescribe medication for a patient."""
        if self.user_role != "doctor":
            QMessageBox.warning(self, "Unauthorized", "Only doctors can prescribe medication.")
            return

        patient_id = self.patient_dropdown.currentData()
        medication = self.medication_input.toPlainText()

        if not patient_id or not medication:
            QMessageBox.warning(self, "Validation Error", "Please select a patient and enter medication details.")
            return

        try:
            api_url = os.getenv("PRESCRIBE_MEDICATION_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "patient_id": patient_id,
                "medication": medication,
                "prescribed_by": self.user_id
            }
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Medication prescribed successfully.")
                self.load_prescriptions()
            else:
                QMessageBox.critical(self, "Error", "Failed to prescribe medication.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def approve_prescription(self):
        """Allows a pharmacist to approve a prescription."""
        if self.user_role != "pharmacist":
            QMessageBox.warning(self, "Unauthorized", "Only pharmacists can approve prescriptions.")
            return

        selected_row = self.prescription_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a prescription to approve.")
            return

        patient_name = self.prescription_table.item(selected_row, 0).text()
        medication = self.prescription_table.item(selected_row, 2).text()

        try:
            api_url = os.getenv("APPROVE_PRESCRIPTION_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {"patient_name": patient_name, "medication": medication, "approved_by": self.user_id}
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Prescription approved successfully.")
                self.load_prescriptions()
            else:
                QMessageBox.critical(self, "Error", "Failed to approve prescription.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
