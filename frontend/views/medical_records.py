from PySide6.QtWidgets import QComboBox, QTextEdit, QPushButton, QMessageBox
from views.base_view import BaseView
from utils.api_utils import fetch_data, post_data
import os

class MedicalRecords(BaseView):
    def __init__(self, user_role, user_id):
        super().__init__("Medical Records Management", ["Patient", "Diagnoses", "Prescriptions", "Lab Results", "Scans"])
        self.user_role = user_role
        self.user_id = user_id
        self.init_form()
        self.load_patients()

    def init_form(self):
        self.patient_dropdown = QComboBox()
        self.layout().addWidget(self.patient_dropdown)

        self.view_button = QPushButton("View Medical Record")
        self.view_button.clicked.connect(self.load_medical_record)
        self.layout().addWidget(self.view_button)

        if self.user_role in ["doctor", "nurse"]:
            self.notes_input = QTextEdit()
            self.notes_input.setPlaceholderText("Enter medical notes...")
            self.layout().addWidget(self.notes_input)

            self.add_note_button = QPushButton("Add Medical Notes")
            self.add_note_button.clicked.connect(self.add_medical_note)
            self.layout().addWidget(self.add_note_button)

    def load_patients(self):
        patients = fetch_data(os.getenv("ASSIGNED_PATIENTS_URL"), params={"user_id": self.user_id, "role": self.user_role})
        if patients:
            for patient in patients:
                self.patient_dropdown.addItem(patient["name"], patient["id"])

    def load_medical_record(self):
        patient_id = self.patient_dropdown.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient!")
            return
        api_url = os.getenv("MEDICAL_RECORD_URL")
        data = {"patient_id": patient_id}
        record = fetch_data(api_url, data, self.token)
        if record:
            self.populate_table([record])

    def add_medical_note(self):
        patient_id = self.patient_dropdown.currentData()
        notes = self.notes_input.toPlainText().strip()

        if not patient_id or not notes:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid medical note.")
            return

        data = {"user_id": self.user_id, "patient_id": patient_id, "notes": notes}
        if post_data(os.getenv("ADD_MEDICAL_NOTE_URL"), data):
            QMessageBox.information(self, "Success", "Medical note added successfully!")
            self.notes_input.clear()