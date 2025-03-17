import os
from PySide6.QtWidgets import (QApplication,
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QGroupBox,
    QHeaderView, QTableWidgetItem, QMessageBox, QLineEdit, QComboBox,
    QFormLayout, QHBoxLayout, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from utils.api_utils import fetch_data, post_data, update_data
from utils.load_auth_cred import LoadAuthCred

class DoctorManagement(QWidget):
    def __init__(self, role, user_id, token):
        super().__init__()
        self.token = token
        self.user_id = user_id
        self.user_role = role
        
        self.setWindowTitle("Patient Management")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(800, 600)  # Set a reasonable minimum size
        self.init_ui()

    def init_ui(self):
        """Initialize UI elements with enhanced styling."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Title Label
        self.title_label = QLabel("Doctor Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            border-bottom: 2px solid #3498db;
        """)
        main_layout.addWidget(self.title_label)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search doctors...")
        self.search_bar.setStyleSheet("""
            padding: 10px;
            border: 1px solid #dcdcdc;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.search_bar.textChanged.connect(self.filter_doctors)
        main_layout.addWidget(self.search_bar)

        # Doctor Table
        self.doctor_table = QTableWidget()
        self.doctor_table.setColumnCount(4)
        self.doctor_table.setHorizontalHeaderLabels(["ID", "Name", "Specialization", "Actions"])
        self.doctor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.doctor_table.setAlternatingRowColors(True)
        self.doctor_table.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                gridline-color: #ddd;
                font-size: 14px;
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.doctor_table)

        # Buttons for Admin
        if self.user_role in ["admin", "nurse", "receptionist"]:
            button_layout = QHBoxLayout()
            
            self.refresh_button = QPushButton("Refresh Doctors")
            self.refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
            self.refresh_button.setStyleSheet(self.button_style())
            self.refresh_button.clicked.connect(self.load_doctors)
            button_layout.addWidget(self.refresh_button)

            self.register_doctor_button = QPushButton("Register New Doctor")
            self.register_doctor_button.setIcon(QIcon("assets/icons/add.png"))
            self.register_doctor_button.setStyleSheet(self.button_style())
            self.register_doctor_button.clicked.connect(self.show_registration_form)
            button_layout.addWidget(self.register_doctor_button)

            main_layout.addLayout(button_layout)
            self.load_doctors()
        elif self.user_role == "doctor":
            self.load_logged_doctors(self.user_id)
        else:
            QMessageBox.critical(self, "Unauthorized", "You are not authorized to access this page")
            return
        self.setLayout(main_layout)
        
    
    def load_logged_doctors(self, user_id):
        """Fetch doctor data from API."""
        base_url = os.getenv("DOCTOR_LIST_URL")
        api_url = f"{base_url}{user_id}"
        doctor = fetch_data(self, api_url, self.token)
        self.populate_table(doctor)
        

    def load_doctors(self):
        """Fetch doctor data from API."""
        api_url = os.getenv("DOCTOR_LIST_URL")
        doctors = fetch_data(self, api_url, self.token)
        self.populate_table(doctors)

    def populate_table(self, doctors):
        """Populate table with doctor data."""
        if isinstance(doctors, dict):  # If a single doctor object is returned
            doctors = [doctors]  # Convert it into a list
            
        self.doctor_table.setRowCount(len(doctors))
        for row, doctor in enumerate(doctors):
            self.doctor_table.setItem(row, 0, QTableWidgetItem(str(doctor["id"])))
            self.doctor_table.setItem(row, 1, QTableWidgetItem(doctor["full_name"]))
            self.doctor_table.setItem(row, 2, QTableWidgetItem(doctor["specialization"]))
            
            if self.user_role == "doctor":
                view_patient_button = QPushButton(f"All Doctor {doctor['full_name']} patients")
                view_patient_button.setStyleSheet(self.button_style(small=True))
                view_patient_button.clicked.connect(lambda checked, d_id=doctor["id"], d_name=doctor["full_name"]: 
                                                self.view_assigned_patients(d_id, d_name))
            else:
                view_patient_button = QPushButton("You Are not a Doctor")
                view_patient_button.setEnabled(False)
                view_patient_button.setToolTip("Only Doctor can view Patients")
            # View Patients Button
            self.doctor_table.setCellWidget(row, 3, view_patient_button)
            
        
       

    def view_assigned_patients(self, doctor_id, doctor_name):
        """Open a window to display patients assigned to a doctor."""
        self.patient_list_window = PatientListWindow(doctor_id, doctor_name)
        self.patient_list_window.show()

    def button_style(self, small=False):
        """Return a consistent button style with hover effects."""
        size = "padding: 8px 15px;" if not small else "padding: 5px 10px;"
        return f"""
            QPushButton {{
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                {size}
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
        """

    def filter_doctors(self):
        """Filter doctors based on search text."""
        search_text = self.search_bar.text().lower()
        for row in range(self.doctor_table.rowCount()):
            match = False
            for col in range(self.doctor_table.columnCount()):
                item = self.doctor_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.doctor_table.setRowHidden(row, not match)

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
        """Initialize UI components with enhanced styling."""
        self.setWindowTitle("Register New Doctor")
        self.setFixedSize(450, 500)  # Set fixed window size

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title Label
        title_label = QLabel("Doctor Registration")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
            text-align: center;
        """)
        layout.addWidget(title_label)

        # Form Layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Name Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Doctor Name")
        self.name_input.setStyleSheet(self.input_style())
        form_layout.addRow("Full Name:", self.name_input)

        # Specialization Dropdown
        self.specialization_input = QComboBox()
        self.specialization_input.addItems(["Cardiology", "Neurology", "Pediatrics", "Oncology", "General Medicine"])
        self.specialization_input.setStyleSheet(self.combo_style())
        form_layout.addRow("Specialization:", self.specialization_input)

        # Contact Number
        self.contact_number = QLineEdit()
        self.contact_number.setPlaceholderText("Enter Contact Number")
        self.contact_number.setStyleSheet(self.input_style())
        form_layout.addRow("Contact Number:", self.contact_number)

        # Email Input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Email Address")
        self.email_input.setStyleSheet(self.input_style())
        form_layout.addRow("Email:", self.email_input)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.input_style())
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        # Display User ID
        self.user_id_label = QLabel(f"Linked User ID: {self.user_id}")
        self.user_id_label.setStyleSheet("font-size: 14px; color: gray; margin-top: 5px;")
        layout.addWidget(self.user_id_label)

        # Button Layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Cancel Button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(QIcon("assets/icons/cancel.png"))
        self.cancel_button.setStyleSheet(self.button_style(cancel=True))
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        # Register Button
        self.submit_button = QPushButton("Register Doctor")
        self.submit_button.setIcon(QIcon("assets/icons/add.png"))
        self.submit_button.setStyleSheet(self.button_style())
        self.submit_button.clicked.connect(self.register_doctor)
        button_layout.addWidget(self.submit_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def register_doctor(self):
        """Send doctor registration data to API with enhanced validation."""
        name = self.name_input.text().strip()
        specialization = self.specialization_input.currentText()
        contact = self.contact_number.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        # Input Validation
        if not name or not specialization or not contact or not email or not password:
            QMessageBox.warning(self, "Validation Error", "All fields are required!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email!")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters long!")
            return

        api_url = os.getenv("REGISTER_DOCTOR_URL")
        data = {
            "full_name": name,
            "specialization": specialization,
            "contact_number": contact,
            "email": email,
            "password": password
        }
        
        if post_data(self, api_url, data, self.token):
            QMessageBox.information(self, "Success", "Doctor registered successfully!")
            self.parent.load_doctors()  # Refresh UI
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to register doctor.")

    @staticmethod
    def input_style():
        """Return CSS for input fields."""
        return """
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #007BFF;
                background-color: #ffffff;
            }
        """

    @staticmethod
    def combo_style():
        """Return CSS for combo box fields."""
        return """
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QComboBox:focus {
                border: 1px solid #007BFF;
                background-color: #ffffff;
            }
        """

    @staticmethod
    def button_style(cancel=False):
        """Return CSS for the buttons."""
        if cancel:
            return """
                QPushButton {
                    padding: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    background-color: #dc3545;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """
        else:
            return """
                QPushButton {
                    padding: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    background-color: #007BFF;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """

class PatientListWindow(QWidget):
    def __init__(self, doctor_id, doctor_name):
        super().__init__()
        self.doctor_id = doctor_id
        self.doctor_name = doctor_name
        self.token = LoadAuthCred.load_auth_token(self)

        self.setWindowTitle("Assigned Patients")
        self.setGeometry(200, 200, 800, 600)  # Slightly larger window for better spacing
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdcdc;
                gridline-color: #dcdcdc;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #007bff; 
                color: white;
                border: none;
                font-size: 14px;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007bff;
            }
        """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title Label
        self.title_label = QLabel(f"Patients Assigned to Dr. {self.doctor_name}")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            border-bottom: 2px solid #3498db;
        """)
        layout.addWidget(self.title_label)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search patients...")
        self.search_bar.textChanged.connect(self.filter_patients)
        layout.addWidget(self.search_bar)

        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(7)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Name", "DOB", "Contact", "Emergency", "Category", "Actions"])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patient_table.setAlternatingRowColors(True)
        self.patient_table.setStyleSheet("QTableWidget::item { padding: 10px; }")
        layout.addWidget(self.patient_table)

        # Back Button
        back_button = QPushButton("Back")
        back_button.setIcon(QIcon("assets/icons/back.png"))
        back_button.clicked.connect(self.close)
        layout.addWidget(back_button, alignment=Qt.AlignLeft)

        self.load_assigned_patients()
        self.setLayout(layout)

    def load_assigned_patients(self):
        """Fetch and display patients assigned to the doctor."""
        base_url = os.getenv("ASSIGNED_PATIENTS_URL")
        api_url = f"{base_url}/{self.doctor_id}/patients"
        patients = fetch_data(self, api_url, self.token)

        if not patients:
            QMessageBox.information(self, "No Patients", "No patients have been assigned yet.")
            return

        self.patient_table.setRowCount(len(patients))
        for row, patient in enumerate(patients):
            self.patient_table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
            self.patient_table.setItem(row, 1, QTableWidgetItem(patient["full_name"]))
            self.patient_table.setItem(row, 2, QTableWidgetItem(patient["date_of_birth"]))
            self.patient_table.setItem(row, 3, QTableWidgetItem(patient["contact_number"]))
            self.patient_table.setItem(row, 4, QTableWidgetItem(str(patient["emergency"])))
            self.patient_table.setItem(row, 5, QTableWidgetItem(patient["category"]))
            
            # Button to View Patient Record
            self.patient_table.setCellWidget(row, 6, self.create_view_button(patient["id"]))

    def create_view_button(self, patient_id):
        """Create 'View Record' button for each patient."""
        button = QPushButton("View Record")
        button.setIcon(QIcon("assets/icons/view.png"))
        button.clicked.connect(lambda: self.open_patient_record(patient_id))
        return button

    def open_patient_record(self, patient_id):
        """Open the patient record management window."""
        self.patient_record_window = PatientRecordUpdateWindow(patient_id)
        self.patient_record_window.show()
        self.close()

    def filter_patients(self):
        """Filter patients based on search text."""
        search_text = self.search_bar.text().lower()
        for row in range(self.patient_table.rowCount()):
            match = False
            for col in range(self.patient_table.columnCount()):
                item = self.patient_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.patient_table.setRowHidden(row, not match)


class PatientRecordUpdateWindow(QWidget):
    def __init__(self, patient_id):
        super().__init__()
        self.patient_id = patient_id
        self.token = LoadAuthCred.load_auth_token(self)
        self.doctor_id = LoadAuthCred.load_user_id(self)
        self.setWindowTitle(f"Patient Record - {patient_id}")
        self.setGeometry(250, 250, 800, 700)  # Slightly larger window for better spacing
        self.init_ui()

    def init_ui(self):
        """Initialize UI components for displaying and updating patient records."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: #fff;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title Label
        self.title_label = QLabel(f"Patient Record - ID: {self.patient_id}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0056b3;")
        main_layout.addWidget(self.title_label)

        # Group Box for Patient Info
        info_group = QGroupBox("Patient Information")
        info_layout = QFormLayout()
        
        self.patient_name_label = QLabel("Loading...")
        self.patient_dob_label = QLabel("Loading...")
        info_layout.addRow("Name:", self.patient_name_label)
        info_layout.addRow("Date of Birth:", self.patient_dob_label)
        info_group.setLayout(info_layout)
        
        # Group Box for Medical Records
        records_group = QGroupBox("Medical Records")
        records_layout = QFormLayout()
        
        # Medical Record Fields
        self.medical_history_text = QTextEdit()
        self.diagnosis_text = QTextEdit()
        self.treatment_plan_text = QTextEdit()
        self.prescription_text = QTextEdit()
        self.lab_tests_text = QTextEdit()
        self.lab_tests_results_text = QTextEdit()
        self.scan_requested_text = QTextEdit()
        self.scan_results_text = QTextEdit()
        self.notes_text = QTextEdit()

        self.medical_history_text.setPlaceholderText("Enter medical history...")
        self.diagnosis_text.setPlaceholderText("Enter diagnosis...")
        self.treatment_plan_text.setPlaceholderText("Enter treatment plan...")
        self.prescription_text.setPlaceholderText("Enter prescriptions...")
        self.lab_tests_text.setPlaceholderText("Requested lab tests...")
        self.lab_tests_results_text.setPlaceholderText("Enter Lab tests results...")
        self.scan_requested_text.setPlaceholderText("Requested scans...")
        self.scan_results_text.setPlaceholderText("Enter scan results...")
        self.notes_text.setPlaceholderText("Additional notes...")

        # Adding fields to layout
        records_layout.addRow("Medical History:", self.medical_history_text)
        records_layout.addRow("Diagnosis:", self.diagnosis_text)
        records_layout.addRow("Treatment Plan:", self.treatment_plan_text)
        records_layout.addRow("Prescription:", self.prescription_text)
        records_layout.addRow("Lab Tests Requested:", self.lab_tests_text)
        records_layout.addRow("Lab Tests Results:", self.lab_tests_results_text)
        records_layout.addRow("Scan Requested:", self.scan_requested_text)
        records_layout.addRow("Scan Results:", self.scan_results_text)
        records_layout.addRow("Notes:", self.notes_text)
        records_group.setLayout(records_layout)

        main_layout.addWidget(info_group)
        main_layout.addWidget(records_group)

        # Buttons Section
        button_layout = QHBoxLayout()
        
        self.create_record_button = QPushButton("Create Medical Record")
        self.update_record_button = QPushButton("Update Medical Record")
        self.cancel_button = QPushButton("Cancel")

        # Connecting Buttons
        self.create_record_button.clicked.connect(self.create_medical_record)
        self.update_record_button.clicked.connect(self.update_medical_record)
        self.cancel_button.clicked.connect(self.close)

        # Adding buttons to layout
        button_layout.addWidget(self.create_record_button)
        button_layout.addWidget(self.update_record_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Load patient details
        self.load_patient_data()

    def load_patient_data(self):
        """Fetch patient details from API and populate fields."""
        base_url = os.getenv("PATIENT_LIST_URL")
        api_url = f"{base_url}{self.patient_id}"
        patient = fetch_data(self, api_url, self.token)

        if patient:
            self.patient_name_label.setText(patient["full_name"])
            self.patient_dob_label.setText(patient["date_of_birth"])
        else:
            QMessageBox.warning(self, "Error", "Failed to load patient details.")

        base_url = os.getenv("MEDICAL_RECORD_URL")
        api_url = f"{base_url}/{self.patient_id}"
        records = fetch_data(self, api_url, self.token)

        # Ensure `records` is not an empty list
        if records and isinstance(records, list):
            record = records[0]  # Get the first record
        elif isinstance(records, dict):  # If API returned a dictionary instead
            record = records
        else:
            QMessageBox.warning(self, "Medical Record Unavailable", "This patient's medical record has not been created yet.")
            return

        self.medical_history_text.setPlainText(record.get("medical_history", ""))
        self.diagnosis_text.setPlainText(record.get("diagnosis", ""))
        self.treatment_plan_text.setPlainText(record.get("treatment_plan", ""))
        self.prescription_text.setPlainText(record.get("prescription", ""))
        self.lab_tests_text.setPlainText(record.get("lab_tests_requested", ""))
        self.lab_tests_results_text.setPlainText(record.get("lab_tests_results", ""))
        self.scan_requested_text.setPlainText(record.get("scans_requested", ""))
        self.scan_results_text.setPlainText(record.get("scan_results", ""))
        self.notes_text.setPlainText(record.get("notes", ""))

    def create_medical_record(self):
        """Send updated medical record data to API."""
        base_url = os.getenv("MEDICAL_RECORD_URL")
        api_url = f"{base_url}/{self.patient_id}"
        
        data = {
            "medical_history": self.medical_history_text.toPlainText().strip(),
            "diagnosis": self.diagnosis_text.toPlainText().strip(),
            "treatment_plan": self.treatment_plan_text.toPlainText().strip(),
            "prescription": self.prescription_text.toPlainText().strip(),
            "lab_tests_requested": self.lab_tests_text.toPlainText().strip(),
            "scan_results": self.scan_results_text.toPlainText().strip(),
            "notes": self.notes_text.toPlainText().strip(),
            "scans_requested": self.scan_requested_text.toPlainText().strip(),
            "lab_tests_results": self.lab_tests_results_text.toPlainText().strip()
        }

        success = post_data(self, api_url, data, self.token)
        if success:
            self.load_patient_data()
            QMessageBox.information(self, "Success", "Medical record Created successfully.")
             
            if not self.lab_tests_text:
                return
            else:
                self.submit_lab_test_request()
                
            if not self.scan_requested_text:
                return
            else:
                self.submit_scan_request()
        else:
            QMessageBox.critical(self, "Error", "Failed to Create medical record.")
    
    def update_medical_record(self):
        """Send updated medical record data to API."""
        base_url = os.getenv("MEDICAL_RECORD_URL")
        api_url = f"{base_url}/{self.patient_id}"
        
        _data = {
            "medical_history": self.medical_history_text.toPlainText().strip(),
            "diagnosis": self.diagnosis_text.toPlainText().strip(),
            "treatment_plan": self.treatment_plan_text.toPlainText().strip(),
            "prescription": self.prescription_text.toPlainText().strip(),
            "lab_tests_requested": self.lab_tests_text.toPlainText().strip(),
            "scan_results": self.scan_results_text.toPlainText().strip(),
            "notes": self.notes_text.toPlainText().strip(),
            "scans_requested": self.scan_requested_text.toPlainText().strip(),
            "lab_tests_results": self.lab_tests_results_text.toPlainText().strip()
        }

        success = update_data(self, api_url, _data, self.token)
        if success:
            self.load_patient_data()
            QMessageBox.information(self, "Success", "Medical record updated successfully.")
             
            if not self.lab_tests_text:
                return
            else:
                self.submit_lab_test_request()
                
            if not self.scan_requested_text:
                return
            else:
                self.submit_scan_request()
        else:
            QMessageBox.critical(self, "Error", "Failed to Update medical record.")
    
    def submit_lab_test_request(self):
        """Send the lab test request to the backend."""
        api_url = os.getenv("LAB_TEST_REQUEST_URL")
        
        request_data = {
            "requested_by": self.doctor_id,
            "patient_id": self.patient_id,
            "test_type": self.lab_tests_text.toPlainText().strip(),
            "additional_notes": self.notes_text.toPlainText().strip(),
        }

        success = post_data(self, api_url, request_data, self.token)

        if success:
            QMessageBox.information(self, "Success", "Lab test request submitted successfully.")
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to submit lab test request.")
            
            
    def submit_scan_request(self):
        """Send radiology scan request to the API"""
        scan_type = self.scan_requested_text.toPlainText().strip()
        api_url = os.getenv("RADIOLOGY_SCAN_URL")
       

        data = {
            "patient_id": self.patient_id,
            "requested_by": self.doctor_id,
            "scan_type": scan_type
        }

        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Radiology scan requested successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to request radiology scan.")




class LabTests(QWidget):
    """Dialog for requesting lab tests for a patient."""

    def __init__(self, patient_id, token):
        super().__init__()
        self.patient_id = patient_id
        self.user_id = LoadAuthCred.load_user_id(self)
        self.token = token
        self.setWindowTitle("Request Lab Test")
        self.setGeometry(300, 300, 400, 300)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components for lab test requests."""
        layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel(f"Request Lab Test for Patient ID: {self.patient_id}")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #007BFF;")
        layout.addWidget(self.title_label)

        # Lab Test Selection
        self.lab_test_label = QLabel("Enter Lab Tests:")
        self.lab_test_input = QTextEdit()
        layout.addWidget(self.lab_test_label)
        layout.addWidget(self.lab_test_input)

        # Additional Notes
        self.notes_label = QLabel("Additional Notes:")
        self.notes_text = QTextEdit()
        layout.addWidget(self.notes_label)
        layout.addWidget(self.notes_text)

        # Request Button
        self.request_button = QPushButton("Submit Request")
        self.request_button.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 8px;")
        self.request_button.clicked.connect(self.submit_request)
        layout.addWidget(self.request_button)

        self.setLayout(layout)

    def submit_request(self):
        """Send the lab test request to the backend."""
        api_url = os.getenv("LAB_TEST_REQUEST_URL")
        
        request_data = {
            "requested_by": self.user_id,
            "patient_id": self.patient_id,
            "test_type": self.lab_test_input.toPlainText().strip(),
            "additional_notes": self.notes_text.toPlainText().strip(),
        }

        success = post_data(self, api_url, request_data, self.token)

        if success:
            QMessageBox.information(self, "Success", "Lab test request submitted successfully.")
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to submit lab test request.")


class RequestRadiologyScan(QWidget):
    def __init__(self, patient_id,doctor_id, token):
        super().__init__()
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.token = token
        self.setWindowTitle("Request Radiology Scan")
        self.setGeometry(300, 300, 400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Select Scan Type:")
        self.scan_type_dropdown = QComboBox()
        self.scan_type_dropdown.addItems(["X-Ray", "MRI", "CT Scan", "Ultrasound", "PET Scan"])
        
        self.submit_button = QPushButton("Request Scan")
        self.submit_button.clicked.connect(self.submit_scan_request)

        layout.addWidget(self.label)
        layout.addWidget(self.scan_type_dropdown)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

    def submit_scan_request(self):
        """Send radiology scan request to the API"""
        scan_type = self.scan_type_dropdown.currentText().strip()
        api_url = os.getenv("RADIOLOGY_SCAN_URL")
       

        data = {
            "patient_id": self.patient_id,
            "requested_by": self.doctor_id,
            "scan_type": scan_type
        }

        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Radiology scan requested successfully.")
            #self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to request radiology scan.")