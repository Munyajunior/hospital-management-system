import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QComboBox
from PySide6.QtCore import Qt

class DoctorManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Doctor Management")

        layout = QVBoxLayout()

        self.title_label = QLabel("Doctor Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Doctor Table
        self.doctor_table = QTableWidget()
        self.doctor_table.setColumnCount(4)
        self.doctor_table.setHorizontalHeaderLabels(["ID", "Name", "Specialization", "Actions"])
        layout.addWidget(self.doctor_table)

        # Buttons for actions
        self.refresh_button = QPushButton("Refresh Doctors")
        self.refresh_button.clicked.connect(self.load_doctors)
        layout.addWidget(self.refresh_button)

        self.register_doctor_button = QPushButton("Register New Doctor")
        self.register_doctor_button.clicked.connect(self.show_registration_form)
        layout.addWidget(self.register_doctor_button)

        self.setLayout(layout)

        self.load_doctors()

    def load_doctors(self):
        """Fetch doctor data from API"""
        try:
            api_url = os.getenv("DOCTOR_LIST_URL")
            response = requests.get(api_url)
            if response.status_code == 200:
                doctors = response.json()
                self.populate_table(doctors)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch doctor data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def populate_table(self, doctors):
        """Populate table with doctor data"""
        self.doctor_table.setRowCount(len(doctors))
        for row, doctor in enumerate(doctors):
            self.doctor_table.setItem(row, 0, QTableWidgetItem(str(doctor["id"])))
            self.doctor_table.setItem(row, 1, QTableWidgetItem(doctor["name"]))
            self.doctor_table.setItem(row, 2, QTableWidgetItem(doctor["specialization"]))

            view_patients_button = QPushButton("View Patients")
            view_patients_button.clicked.connect(lambda checked, d_id=doctor["id"]: self.view_assigned_patients(d_id))
            self.doctor_table.setCellWidget(row, 3, view_patients_button)

    def view_assigned_patients(self, doctor_id):
        """View patients assigned to a doctor"""
        try:
            api_url = os.getenv("ASSIGNED_PATIENTS_URL")
            response = requests.get(f"{api_url}/{doctor_id}")
            if response.status_code == 200:
                patients = response.json()
                self.show_assigned_patients(patients)
            else:
                QMessageBox.critical(self, "Error", "Failed to fetch assigned patients.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def show_assigned_patients(self, patients):
        """Display assigned patients in a message box"""
        patient_list = "\n".join([f"{p['id']} - {p['name']} ({p['age']} years)" for p in patients])
        QMessageBox.information(self, "Assigned Patients", f"Patients assigned to doctor:\n\n{patient_list}")

    def show_registration_form(self):
        """Show doctor registration form"""
        self.registration_window = DoctorRegistrationForm(self)
        self.registration_window.show()


class DoctorRegistrationForm(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Register New Doctor")

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Doctor Name")
        layout.addWidget(self.name_input)

        self.specialization_input = QComboBox()
        self.specialization_input.addItems(["Cardiology", "Neurology", "Pediatrics", "Oncology", "General Medicine"])
        layout.addWidget(self.specialization_input)

        self.submit_button = QPushButton("Register Doctor")
        self.submit_button.clicked.connect(self.register_doctor)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def register_doctor(self):
        """Send doctor registration data to API"""
        name = self.name_input.text().strip()
        specialization = self.specialization_input.currentText()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Doctor name is required!")
            return

        try:
            api_url = os.getenv("REGISTER_DOCTOR_URL")
            response = requests.post(api_url, json={"name": name, "specialization": specialization})
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Doctor registered successfully!")
                self.parent.load_doctors()
                self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to register doctor.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
