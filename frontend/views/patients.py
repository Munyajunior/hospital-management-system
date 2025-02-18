import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QComboBox, QInputDialog
from PySide6.QtCore import Qt

class PatientManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Patient Management")
        
        layout = QVBoxLayout()
        
        self.title_label = QLabel("Patient Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(5)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Doctor Assigned", "Actions"])
        layout.addWidget(self.patient_table)

        # Buttons for actions
        self.refresh_button = QPushButton("Refresh Patients")
        self.refresh_button.clicked.connect(self.load_patients)
        layout.addWidget(self.refresh_button)

        self.register_patient_button = QPushButton("Register New Patient")
        self.register_patient_button.clicked.connect(self.show_registration_form)
        layout.addWidget(self.register_patient_button)

        self.setLayout(layout)

        self.load_patients()

    def load_patients(self):
        """Fetch patient data from API"""
        try:
            api_url = os.getenv("PATIENT_LIST_URL")
            response = requests.get(api_url)
            if response.status_code == 200:
                patients = response.json()
                self.populate_table(patients)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch patient data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, patients):
        """Populate table with patient data"""
        self.patient_table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            self.patient_table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
            self.patient_table.setItem(row, 1, QTableWidgetItem(patient["name"]))
            self.patient_table.setItem(row, 2, QTableWidgetItem(str(patient["age"])))
            self.patient_table.setItem(row, 3, QTableWidgetItem(patient.get("doctor", "Not Assigned")))

            assign_button = QPushButton("Assign Doctor")
            assign_button.clicked.connect(lambda checked, p_id=patient["id"]: self.assign_doctor(p_id))
            self.patient_table.setCellWidget(row, 4, assign_button)

    def assign_doctor(self, patient_id):
        """Assign a doctor to a patient"""
        doctor_id, ok = QInputDialog.getInt(self, "Assign Doctor", "Enter Doctor ID:")
        if ok:
            try:
                api_url = os.getenv("ASSIGN_DOCTOR_URL")
                response = requests.post(api_url, json={"patient_id": patient_id, "doctor_id": doctor_id})
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Doctor assigned successfully!")
                    self.load_patients()
                else:
                    QMessageBox.critical(self, "Error", "Failed to assign doctor.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def show_registration_form(self):
        """Show patient registration form"""
        self.registration_window = PatientRegistrationForm(self)
        self.registration_window.show()


class PatientRegistrationForm(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Register New Patient")
        
        layout = QVBoxLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Patient Name")
        layout.addWidget(self.name_input)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Enter Age")
        layout.addWidget(self.age_input)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        layout.addWidget(self.gender_input)

        self.submit_button = QPushButton("Register Patient")
        self.submit_button.clicked.connect(self.register_patient)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def register_patient(self):
        """Send patient registration data to API"""
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        gender = self.gender_input.currentText()

        if not name or not age:
            QMessageBox.warning(self, "Validation Error", "Name and age are required!")
            return

        try:
            api_url = os.getenv("REGISTER_PATIENT_URL")
            response = requests.post(api_url, json={"name": name, "age": age, "gender": gender})
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Patient registered successfully!")
                self.parent.load_patients()
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to register patient.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
