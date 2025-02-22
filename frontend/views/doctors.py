import os
import requests
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QComboBox
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, post_data
from utils.load_auth_cred import LoadAuthCred

class DoctorManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.token = LoadAuthCred.load_auth_token(self)
        self.user_id = LoadAuthCred.load_user_id(self)
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
        api_url = os.getenv("DOCTOR_LIST_URL")
        doctors = fetch_data(api_url,self.token)
        self.populate_table(doctors)
            

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
        api_url = os.getenv(f"ASSIGNED_PATIENTS_URL"+"/{self.user_id}/{patients}")
        patients = fetch_data(api_url,self.token)
        self.show_assigned_patients(patients)
            

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
        self.token = LoadAuthCred.load_auth_token(self)
        self.user_id = int(LoadAuthCred.load_user_id(self))
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
        
        self.contact_number = QLineEdit()
        self.contact_number.setPlaceholderText("Enter Doctor Contact")
        layout.addWidget(self.contact_number)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Doctor Email")
        layout.addWidget(self.email_input)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter Doctor Password")
        layout.addWidget(self.password)

        self.submit_button = QPushButton("Register Doctor")
        self.submit_button.clicked.connect(self.register_doctor)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def register_doctor(self):
        """Send doctor registration data to API"""
        name = self.name_input.text().strip()
        specialization = self.specialization_input.currentText()
        contact = self.contact_number.text().strip()
        email = self.email_input.text().strip()
        password = self.password.text().strip()
        user_id: int = int(self.user_id)

        if not name or not specialization or not contact or not email or not user_id:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return
        
        if "@" not in email:
            QMessageBox.warning(self, "Validation Error", "Please Enter valid Email!")
            return
      
        api_url = os.getenv("REGISTER_DOCTOR_URL")
        data = {
            "full_name": name, 
            "specialization": specialization,
            "contact_number": contact,
            "email": email,
            "hash_password": password,
            "user_id": user_id
        }
        post_data(api_url, data, self.token)
        self.parent.load_doctors()
        self.close()
