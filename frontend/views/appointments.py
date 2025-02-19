import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QDateTimeEdit, QTextEdit
)
from PySide6.QtCore import Qt


class Appointments(QWidget):
    def __init__(self, user_role, user_id):
        """
        Initializes the Appointments Management interface.

        :param user_role: Role of the logged-in user (doctor/nurse)
        :param user_id: ID of the logged-in user (for filtering appointments)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Appointments Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Appointments")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Appointments Table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(4)
        self.appointments_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Date/Time", "Reason"])
        layout.addWidget(self.appointments_table)

        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        layout.addWidget(self.patient_dropdown)

        # Date & Time Picker
        self.datetime_picker = QDateTimeEdit()
        self.datetime_picker.setCalendarPopup(True)
        layout.addWidget(self.datetime_picker)

        # Appointment Reason Input
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Enter appointment reason...")
        layout.addWidget(self.reason_input)

        # Button to schedule appointment
        self.schedule_button = QPushButton("Schedule Appointment")
        self.schedule_button.clicked.connect(self.schedule_appointment)
        layout.addWidget(self.schedule_button)

        # Load existing appointments
        self.load_appointments()

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

    def load_appointments(self):
        """Fetches and displays scheduled appointments."""
        try:
            api_url = os.getenv("APPOINTMENTS_URL")
            response = requests.get(f"{api_url}?user_id={self.user_id}&role={self.user_role}")
            if response.status_code == 200:
                appointments = response.json()
                self.populate_table(appointments)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch appointments.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, appointments):
        """Fills the table with appointment data."""
        self.appointments_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            self.appointments_table.setItem(row, 0, QTableWidgetItem(appointment["patient_name"]))
            self.appointments_table.setItem(row, 1, QTableWidgetItem(appointment["doctor_name"]))
            self.appointments_table.setItem(row, 2, QTableWidgetItem(appointment["datetime"]))
            self.appointments_table.setItem(row, 3, QTableWidgetItem(appointment["reason"]))

    def schedule_appointment(self):
        """Schedules a new appointment."""
        patient_id = self.patient_dropdown.currentData()
        datetime = self.datetime_picker.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        reason = self.reason_input.toPlainText().strip()

        if not patient_id or not reason:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        try:
            api_url = os.getenv("SCHEDULE_APPOINTMENT_URL")
            data = {"doctor_id": self.user_id, "patient_id": patient_id, "datetime": datetime, "reason": reason}
            response = requests.post(api_url, json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Appointment scheduled successfully!")
                self.load_appointments()  # Refresh the table
                self.reason_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to schedule appointment.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
