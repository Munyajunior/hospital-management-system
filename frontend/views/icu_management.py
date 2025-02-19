import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt


class ICUManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the ICU Management interface.

        :param user_role: Role of the logged-in user (admin/nurse/doctor)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.auth_token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ICU & Critical Patient Management")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("ICU & Critical Patient Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # Critical Patients Table
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(5)
        self.patients_table.setHorizontalHeaderLabels(["Patient Name", "Doctor", "Condition", "ICU Room", "Status"])
        self.patients_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.patients_table)

        # ICU Admission Form (Nurses/Admin Only)
        if self.user_role in ["admin", "nurse"]:
            form_layout = QVBoxLayout()

            self.patient_dropdown = QComboBox()
            self.load_patients()
            form_layout.addWidget(self.patient_dropdown)

            self.condition_input = QTextEdit()
            self.condition_input.setPlaceholderText("Enter patient condition details...")
            form_layout.addWidget(self.condition_input)

            self.icu_room_dropdown = QComboBox()
            self.load_available_icu_rooms()
            form_layout.addWidget(self.icu_room_dropdown)

            self.admit_button = QPushButton("Admit Patient to ICU")
            self.admit_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            self.admit_button.clicked.connect(self.admit_patient)
            form_layout.addWidget(self.admit_button)

            layout.addLayout(form_layout)

        # Load Patients Button
        self.load_patients_button = QPushButton("Refresh ICU Patients")
        self.load_patients_button.clicked.connect(self.load_icu_patients)
        self.load_patients_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        layout.addWidget(self.load_patients_button)

        self.load_icu_patients()
        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with non-ICU patients (for admission)."""
        if self.user_role not in ["admin", "nurse"]:
            return

        try:
            api_url = os.getenv("NON_ICU_PATIENTS_URL")
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

    def load_available_icu_rooms(self):
        """Fetches and populates available ICU rooms."""
        if self.user_role not in ["admin", "nurse"]:
            return

        try:
            api_url = os.getenv("AVAILABLE_ICU_ROOMS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                rooms = response.json()
                for room in rooms:
                    self.icu_room_dropdown.addItem(f"Room {room['room_number']} (Bed {room['bed_number']})", room["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch ICU room list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def load_icu_patients(self):
        """Fetches and displays ICU patients."""
        try:
            api_url = os.getenv("ICU_PATIENTS_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(api_url, headers=headers)

            if response.status_code == 200:
                icu_patients = response.json()
                self.populate_table(icu_patients)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch ICU patient list.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, icu_patients):
        """Fills the ICU patient table with data."""
        self.patients_table.setRowCount(len(icu_patients))
        for row, patient in enumerate(icu_patients):
            self.patients_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
            self.patients_table.setItem(row, 1, QTableWidgetItem(patient["doctor_name"]))
            self.patients_table.setItem(row, 2, QTableWidgetItem(patient["condition"]))
            self.patients_table.setItem(row, 3, QTableWidgetItem(f"Room {patient['icu_room']}"))
            self.patients_table.setItem(row, 4, QTableWidgetItem(patient["status"]))

    def admit_patient(self):
        """Admits a patient to the ICU (Nurse/Admin Only)."""
        if self.user_role not in ["admin", "nurse"]:
            QMessageBox.warning(self, "Unauthorized", "Only nurses and admins can admit patients to the ICU.")
            return

        patient_id = self.patient_dropdown.currentData()
        condition = self.condition_input.toPlainText().strip()
        icu_room_id = self.icu_room_dropdown.currentData()

        if not patient_id or not condition or not icu_room_id:
            QMessageBox.warning(self, "Validation Error", "Please fill all fields.")
            return

        try:
            api_url = os.getenv("ADMIT_ICU_PATIENT_URL")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            data = {
                "patient_id": patient_id,
                "condition": condition,
                "icu_room_id": icu_room_id,
                "nurse_id": self.user_id,
            }
            response = requests.post(api_url, json=data, headers=headers)

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Patient successfully admitted to ICU.")
                self.load_icu_patients()
                self.condition_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to admit patient.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
