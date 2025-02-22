import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLineEdit, QComboBox, QInputDialog,
    QDateEdit, QTextEdit
)
from PySide6.QtCore import Qt
from utils.load_auth_cred import LoadAuthCred
from utils.api_utils import fetch_data, post_data
from dotenv import load_dotenv

load_dotenv()


class PatientManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.token = LoadAuthCred.load_auth_token(self)  # Load stored token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Patient Management")
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
            }
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header Label
        self.title_label = QLabel("Patient Management")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(5)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Doctor Assigned", "Actions"])
        self.patient_table.horizontalHeader().setStretchLastSection(True)
        self.patient_table.setStyleSheet("QTableWidget { border: 1px solid #ccc; }")
        main_layout.addWidget(self.patient_table, stretch=1)

        # Buttons Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.refresh_button = QPushButton("Refresh Patients")
        self.refresh_button.clicked.connect(self.load_patients)
        button_layout.addWidget(self.refresh_button)
        
        self.register_patient_button = QPushButton("Register New Patient")
        self.register_patient_button.clicked.connect(self.show_registration_form)
        button_layout.addWidget(self.register_patient_button)
        
        # Center the buttons by adding stretch on both sides
        centered_button_layout = QHBoxLayout()
        centered_button_layout.addStretch(1)
        centered_button_layout.addLayout(button_layout)
        centered_button_layout.addStretch(1)
        
        main_layout.addLayout(centered_button_layout, stretch=0)

        self.setLayout(main_layout)
        self.load_patients()


    def load_patients(self):
        """Fetch patient data from API with Authorization"""
        
        api_url = os.getenv("PATIENT_LIST_URL")
        patients = fetch_data(api_url, self.token)
        self.populate_table(patients)
            

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
        self.registration_window = PatientRegistrationForm(self, self.token)
        self.registration_window.show()


class PatientRegistrationForm(QWidget):
    def __init__(self, parent, token):
        super().__init__()
        self.parent = parent
        self.token = LoadAuthCred.load_auth_token(self)  # Load stored token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Register New Patient")
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            QLineEdit, QDateEdit, QComboBox, QTextEdit {
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
       
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Patient Name")
        layout.addWidget(self.name_input)

        self.age_input = QDateEdit()
        self.age_input.setCalendarPopup(True)
        layout.addWidget(self.age_input)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        layout.addWidget(self.gender_input)
        
        self.contact_number = QLineEdit()
        self.contact_number.setPlaceholderText("Enter Contact Number")
        layout.addWidget(self.contact_number)
        
        self.address = QLineEdit()
        self.address.setPlaceholderText("Enter Address")
        layout.addWidget(self.address)
        
        self.medical_history = QTextEdit()
        self.medical_history.setPlaceholderText("Enter Medical History")
        layout.addWidget(self.medical_history)

        # Doctor Selection
        self.doctor_input = QComboBox()
        self.load_doctors()
        layout.addWidget(self.doctor_input)

        self.submit_button = QPushButton("Register Patient")
        self.submit_button.clicked.connect(self.register_patient)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        
    def load_doctors(self):
        """Fetch list of doctors from API"""
        
        api_url = os.getenv("DOCTOR_LIST_URL")
        doctors = fetch_data(api_url, self.token)
        if doctors is None:
            self.doctor_input.addItem("Select Doctor", None)
            for doctor in doctors:
                self.doctor_input.addItem(f"{doctor['full_name']} (ID: {doctor['id']})", doctor["id"])
        

    def register_patient(self):
        """Send patient registration data to API"""
        name = self.name_input.text().strip()
        dob = self.age_input.date().toString("yyyy-MM-dd")
        gender = self.gender_input.currentText()
        contact_number = self.contact_number.text().strip()
        address = self.address.text().strip()
        medical_history = self.medical_history.toPlainText().strip()
        assigned_doctor_id = self.doctor_input.currentData()

        if not name or not dob or not contact_number or not address:
            QMessageBox.warning(self, "Validation Error", "All fields except medical history are required!")
            return

        
        api_url = os.getenv("REGISTER_PATIENT_URL")
        data = {
            "full_name": name,
            "date_of_birth": dob,
            "gender": gender,
            "contact_number": contact_number,
            "address": address,
            "medical_history": medical_history,
            "assigned_doctor_id": assigned_doctor_id
        }
        register = post_data(api_url,data,self.token)
        if register == True: 
            QMessageBox.information(self, "Success", "Patient registered successfully!")
            self.parent.load_patients()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to register patient.")
        
