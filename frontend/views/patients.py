import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLineEdit, QComboBox, QInputDialog,
    QDateEdit, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.load_auth_cred import LoadAuthCred
from utils.api_utils import fetch_data, post_data
from dotenv import load_dotenv

load_dotenv()


class PatientManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.token = LoadAuthCred.load_auth_token(self)  # Load stored token
        self.doctor_dict = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Patient Management")
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel#titleLabel {
                font-size: 26px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                border-bottom: 2px solid #3498db;
                text-align: center;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdcdc;
                font-size: 14px;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e6fa7;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

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
        self.patient_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.patient_table, stretch=1)

        # Buttons Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.refresh_button = QPushButton("Refresh Patients")
        self.refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.refresh_button.clicked.connect(self.load_patients)
        button_layout.addWidget(self.refresh_button)

        self.register_patient_button = QPushButton("Register New Patient")
        self.register_patient_button.setIcon(QIcon("assets/icons/add.png"))
        self.register_patient_button.clicked.connect(self.show_registration_form)
        button_layout.addWidget(self.register_patient_button)

        # Center the buttons
        centered_button_layout = QHBoxLayout()
        centered_button_layout.addStretch(1)
        centered_button_layout.addLayout(button_layout)
        centered_button_layout.addStretch(1)

        main_layout.addLayout(centered_button_layout, stretch=0)

        self.setLayout(main_layout)
        self.load_doctor_list()
        self.load_patients()

    def load_patients(self):
        """Fetch patient data from API with Authorization"""
        api_url = os.getenv("PATIENT_LIST_URL")
        patients = fetch_data(self, api_url, self.token)
        self.populate_table(patients)

    def load_doctor_list(self):
        """Fetch all doctors and store them in a dictionary {doctor_id: doctor_name}"""
        api_url = os.getenv("DOCTOR_LIST_URL")
        doctors = fetch_data(self, api_url, self.token)
        self.doctor_dict = {doctor["id"]: doctor["full_name"] for doctor in doctors} if doctors else {}

    def populate_table(self, patients):
        """Populate table with patient data, displaying doctor names instead of just IDs"""
        self.patient_table.setRowCount(len(patients))

        for row, patient in enumerate(patients):
            self.patient_table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
            self.patient_table.setItem(row, 1, QTableWidgetItem(patient["full_name"]))
            self.patient_table.setItem(row, 2, QTableWidgetItem(str(patient["date_of_birth"])))

            doctor_id = patient.get("assigned_doctor_id")
            if doctor_id and doctor_id in self.doctor_dict:
                doctor_name = self.doctor_dict[doctor_id]
                self.patient_table.setItem(row, 3, QTableWidgetItem(f"{doctor_name} (ID: {doctor_id})"))
            else:
                self.patient_table.setItem(row, 3, QTableWidgetItem("Not Assigned"))

            # Assign Doctor Button
            assign_button = QPushButton("Assign Doctor")
            assign_button.setIcon(QIcon("assets/icons/doctor.png"))
            assign_button.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
                QPushButton:disabled {
                    background-color: #95a5a6;
                }
            """)

            if doctor_id:
                assign_button.setEnabled(False)
                assign_button.setToolTip("Doctor already assigned")
            else:
                assign_button.clicked.connect(lambda checked, p_id=patient["id"]: self.assign_doctor(p_id))

            self.patient_table.setCellWidget(row, 4, assign_button)

    def assign_doctor(self, patient_id):
        """Assign a doctor to a patient"""
        doctor_names = list(self.doctor_dict.values())

        selected_row = self.patient_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "No Selection", "Please select a patient to assign a doctor.")
            return

        patient_id = self.patient_table.item(selected_row, 0).text()
        selected_index, ok = QInputDialog.getItem(self, "Select Doctor", "Choose a doctor:", doctor_names, 0, False)
        if ok and selected_index:
            doctor_name = selected_index
            doctor_id = [key for key, value in self.doctor_dict.items() if value == doctor_name][0]

            try:
                base_url = os.getenv("ASSIGN_DOCTOR_URL")
                api_url = f"{base_url}/{patient_id}/assign/{doctor_id}"
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

                response = requests.put(api_url, headers=headers, json={"patient_id": patient_id, "doctor_id": doctor_id})
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Doctor assigned successfully!")
                    self.load_doctor_list()
                    self.load_patients()
                else:
                    error_msg = response.json().get("detail", "Failed to assign doctor.")
                    QMessageBox.critical(self, "Error", f"Error: {error_msg}")
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
        """Fetch list of doctors from API and populate the combo box."""
        api_url = os.getenv("DOCTOR_LIST_URL")
        doctors = fetch_data(self, api_url, self.token)
        self.doctor_input.clear()
        self.doctor_input.addItem("Select Doctor", None)
        if doctors:
            for doctor in doctors:
                self.doctor_input.addItem(f"{doctor['full_name']} (ID: {doctor['id']})", doctor["id"])
        else:
            QMessageBox.warning(self, "Warning", "No doctors found or failed to fetch doctor data.")

        

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
        register = post_data(self, api_url,data,self.token)
        if register: 
            QMessageBox.information(self, "Success", "Patient registered successfully!")
            self.parent.load_doctor_list()
            self.parent.load_patients()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to register patient.")
        
