import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QComboBox, QDateTimeEdit
from PySide6.QtCore import Qt

class AppointmentManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Appointment Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Manage Appointments")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Appointment Table
        self.appointment_table = QTableWidget()
        self.appointment_table.setColumnCount(5)
        self.appointment_table.setHorizontalHeaderLabels(["ID", "Patient", "Doctor", "Date & Time", "Status"])
        layout.addWidget(self.appointment_table)

        # Buttons for actions
        self.refresh_button = QPushButton("Refresh Appointments")
        self.refresh_button.clicked.connect(self.load_appointments)
        layout.addWidget(self.refresh_button)

        self.schedule_button = QPushButton("Schedule New Appointment")
        self.schedule_button.clicked.connect(self.show_schedule_form)
        layout.addWidget(self.schedule_button)

        self.setLayout(layout)

        self.load_appointments()

    def load_appointments(self):
        """Fetch appointment data from API"""
        try:
            api_url = os.getenv("APPOINTMENT_LIST_URL")
            response = requests.get(api_url)
            if response.status_code == 200:
                appointments = response.json()
                self.populate_table(appointments)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch appointment data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, appointments):
        """Populate table with appointment data"""
        self.appointment_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            self.appointment_table.setItem(row, 0, QTableWidgetItem(str(appointment["id"])))
            self.appointment_table.setItem(row, 1, QTableWidgetItem(appointment["patient_name"]))
            self.appointment_table.setItem(row, 2, QTableWidgetItem(appointment["doctor_name"]))
            self.appointment_table.setItem(row, 3, QTableWidgetItem(appointment["datetime"]))
            self.appointment_table.setItem(row, 4, QTableWidgetItem(appointment["status"]))

    def show_schedule_form(self):
        """Show appointment scheduling form"""
        self.schedule_window = AppointmentScheduleForm(self)
        self.schedule_window.show()


class AppointmentScheduleForm(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Schedule Appointment")

        layout = QVBoxLayout()

        self.patient_input = QComboBox()
        self.load_patients()
        layout.addWidget(self.patient_input)

        self.doctor_input = QComboBox()
        self.load_doctors()
        layout.addWidget(self.doctor_input)

        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        layout.addWidget(self.datetime_input)

        self.submit_button = QPushButton("Schedule Appointment")
        self.submit_button.clicked.connect(self.schedule_appointment)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def load_patients(self):
        """Fetch patient list from API"""
        try:
            api_url = os.getenv("PATIENT_LIST_URL")
            response = requests.get(api_url)
            if response.status_code == 200:
                patients = response.json()
                for patient in patients:
                    self.patient_input.addItem(patient["name"], patient["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch patients.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def load_doctors(self):
        """Fetch doctor list from API"""
        try:
            api_url = os.getenv("DOCTOR_LIST_URL")
            response = requests.get(api_url)
            if response.status_code == 200:
                doctors = response.json()
                for doctor in doctors:
                    self.doctor_input.addItem(doctor["name"], doctor["id"])
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch doctors.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def schedule_appointment(self):
        """Send appointment scheduling data to API"""
        patient_id = self.patient_input.currentData()
        doctor_id = self.doctor_input.currentData()
        appointment_datetime = self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if not patient_id or not doctor_id:
            QMessageBox.warning(self, "Validation Error", "Please select both patient and doctor!")
            return

        try:
            api_url = os.getenv("SCHEDULE_APPOINTMENT_URL")
            response = requests.post(api_url, json={"patient_id": patient_id, "doctor_id": doctor_id, "datetime": appointment_datetime})
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Appointment scheduled successfully!")
                self.parent.load_appointments()
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to schedule appointment.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
