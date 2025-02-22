from PySide6.QtWidgets import QComboBox, QDateTimeEdit, QTextEdit, QPushButton, QMessageBox
from views.base_view import BaseView
from utils.api_utils import fetch_data, post_data
import os

class Appointments(BaseView):
    def __init__(self, user_role, user_id):
        super().__init__("Appointments Management", ["Patient", "Doctor", "Date/Time", "Reason"])
        self.user_role = user_role
        self.user_id = user_id
        self.init_form()
        self.load_appointments()

    def init_form(self):
        self.patient_dropdown = QComboBox()
        self.load_patients()
        self.layout().addWidget(self.patient_dropdown)

        self.datetime_picker = QDateTimeEdit()
        self.datetime_picker.setCalendarPopup(True)
        self.layout().addWidget(self.datetime_picker)

        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Enter appointment reason...")
        self.layout().addWidget(self.reason_input)

        self.schedule_button = QPushButton("Schedule Appointment")
        self.schedule_button.clicked.connect(self.schedule_appointment)
        self.layout().addWidget(self.schedule_button)

    def load_patients(self):
        patients = fetch_data(os.getenv("ASSIGNED_PATIENTS_URL"), params={"user_id": self.user_id, "role": self.user_role})
        if patients:
            for patient in patients:
                self.patient_dropdown.addItem(patient["name"], patient["id"])

    def load_appointments(self):
        appointments = fetch_data(os.getenv("APPOINTMENTS_URL"), params={"user_id": self.user_id, "role": self.user_role})
        if appointments:
            self.populate_table(appointments)

    def schedule_appointment(self):
        patient_id = self.patient_dropdown.currentData()
        datetime = self.datetime_picker.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        reason = self.reason_input.toPlainText().strip()

        if not patient_id or not reason:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        data = {"doctor_id": self.user_id, "patient_id": patient_id, "datetime": datetime, "reason": reason}
        if post_data(os.getenv("SCHEDULE_APPOINTMENT_URL"), data):
            QMessageBox.information(self, "Success", "Appointment scheduled successfully!")
            self.load_appointments()
            self.reason_input.clear()