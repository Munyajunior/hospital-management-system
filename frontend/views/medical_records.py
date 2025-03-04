from PySide6.QtWidgets import QWidget, QHeaderView, QPushButton, QMessageBox, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QScrollArea
from .doctors import PatientRecordUpdateWindow
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, post_data
import os

class MedicalRecords(QWidget):
    def __init__(self, user_role, user_id, token):
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        
        self.setWindowTitle("Patient Management")
        self.setGeometry(300, 200, 800, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Arial', sans-serif;
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
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::horizontalHeader {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::horizontalHeader::section {
                padding-left: 10px;
                padding-right: 10px;
                text-align: center;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e6fa7;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
           
        """)
        self.init_ui()
        
    def init_ui(self):     
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        
        # Header Label
        self.title_label = QLabel("Medical Records")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        if self.user_role == "doctor":

            # Patient Table
            self.medical_record_table = QTableWidget()
            self.medical_record_table.setColumnCount(4)
            self.medical_record_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Actions"])
            self.medical_record_table.horizontalHeader().setStretchLastSection(True)
            self.medical_record_table.setAlternatingRowColors(True)
            main_layout.addWidget(self.medical_record_table, stretch=1)
            
            self.load_assigned_patients()
            self.setLayout(main_layout)
            
        else:
             # Create scrollable table
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)  # Allow resizing

            # Patient Table
            self.patient_table = QTableWidget()
            self.patient_table.setColumnCount(14)
            self.patient_table.setHorizontalHeaderLabels([
                "ID", "Name", "Date of Birth", "Gender", "Contact Number",
                "Address", "Medical History", "Diagnosis", "Treatment Plan",
                "Prescription", "Lab Tests", "Radiography", "Notes", "Actions"
            ])

            # Enable word wrap for header labels
            self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
            self.patient_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.TextWordWrap)  # Enables text wrapping

            # Adjust row height dynamically for better readability
            self.patient_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            # resize mode for column headers
            self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            # Set alternating row colors for readability
            self.patient_table.setAlternatingRowColors(True)

            # Set column width for "Actions" column
            self.patient_table.setColumnWidth(13, 350)

            # Enable scrolling
            self.patient_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.patient_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            # Add table inside the scroll area
            self.scroll_area.setWidget(self.patient_table)
            main_layout.addWidget(self.scroll_area)
            
            self.load_assigned_patients()
            self.setLayout(main_layout)


    def load_assigned_patients(self):
        if self.user_role == "doctor":
            doctor_id = self.user_id
            base_url = os.getenv("ASSIGNED_PATIENTS_URL")
            api_url = f"{base_url}/{doctor_id}/patients"
            patients = fetch_data(self, api_url, self.token)

            if not patients:
                QMessageBox.information(self, "No Patients", "No patients have been assigned yet.")
                return

            self.medical_record_table.setRowCount(len(patients))
            for row, patient in enumerate(patients):
                self.medical_record_table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
                self.medical_record_table.setItem(row, 1, QTableWidgetItem(patient["full_name"]))
                self.medical_record_table.setItem(row, 2, QTableWidgetItem(patient["date_of_birth"]))

                # Button to View Patient Record
                self.medical_record_table.setCellWidget(row, 3, self.create_view_button(patient["id"]))

        else:
            base_url = os.getenv("MEDICAL_RECORD_URL")
            api_url = f"{base_url}/"
            patients = fetch_data(self, api_url, self.token)
            
            if not patients:
                QMessageBox.information(self, "No Patients", "No patients Have been Registered.")
                return
            self.patient_table.setRowCount(len(patients))
            for row, patient in enumerate(patients):
                self.patient_table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
                self.patient_table.setItem(row, 1, QTableWidgetItem(patient["full_name"]))
                self.patient_table.setItem(row, 2, QTableWidgetItem(patient["date_of_birth"]))
                self.patient_table.setItem(row, 3, QTableWidgetItem(patient["gender"]))
                self.patient_table.setItem(row, 4, QTableWidgetItem(patient["contact_number"]))
                self.patient_table.setItem(row, 5, QTableWidgetItem(patient["address"]))
                self.patient_table.setItem(row, 6, QTableWidgetItem(patient["medical_history"]))
                self.patient_table.setItem(row, 7, QTableWidgetItem(patient["diagnosis"]))
                self.patient_table.setItem(row, 8, QTableWidgetItem(patient["treatment_plan"]))
                self.patient_table.setItem(row, 9, QTableWidgetItem(patient["prescription"]))
                self.patient_table.setItem(row, 10, QTableWidgetItem(patient["lab_tests_results"]))
                self.patient_table.setItem(row, 11, QTableWidgetItem(patient["scan_results"]))
                self.patient_table.setItem(row, 12, QTableWidgetItem(patient["notes"]))
                # Button to View Patient Record
                self.patient_table.setCellWidget(row, 13, self.update_view_button(patient["id"]))
            
            
    def update_view_button(self, patient_id):
        """Create 'View Record' button for each patient."""
        button = QPushButton("Update Record")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.update_patient_record(patient_id))
        return button

    def update_patient_record(self, patient_id):
        """Open the patient record management window."""
        self.patient_record_window = PatientRecordUpdateWindow(patient_id)
        self.patient_record_window.show()
        
    def create_view_button(self, patient_id):
        """Create 'View Record' button for each patient."""
        button = QPushButton("View Record")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.open_patient_record(patient_id))
        return button

    def open_patient_record(self, patient_id):
        """Open the patient record management window."""
        self.patient_record_window = PatientRecordWindow(patient_id, self.user_id, self.token)
        self.patient_record_window.show()
    
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
        
    # def load_medical_record(self):
    #     patient_id = self.patient_dropdown.currentData()
    #     if not patient_id:
    #         QMessageBox.warning(self, "Validation Error", "Please select a patient!")
    #         return
    #     base_url = os.getenv("MEDICAL_RECORD_URL")
    #     api_url = f"{base_url}/{patient_id}"
        
    #     record = fetch_data(api_url, self.token)
    #     if record:
    #         self.populate_table([record])
        

    # def add_medical_note(self):
    #     patient_id = self.patient_dropdown.currentData()
    #     notes = self.notes_input.toPlainText().strip()

    #     if not patient_id or not notes:
    #         QMessageBox.warning(self, "Validation Error", "Please enter a valid medical note.")
    #         return

    #     data = {"user_id": self.user_id, "patient_id": patient_id, "notes": notes}
    #     if post_data(os.getenv("ADD_MEDICAL_NOTE_URL"), data):
    #         QMessageBox.information(self, "Success", "Medical note added successfully!")
    #         self.notes_input.clear()
    
    

class PatientRecordWindow(QWidget):
    def __init__(self, patient_id, user_id, token):
        super().__init__()
        self.patient_id = patient_id
        self.token = token
        self.doctor_id = user_id
        self.setWindowTitle(f"Patient Record - {patient_id}")
        self.setGeometry(250, 250, 750, 650)
        self.init_ui()

    def init_ui(self):
        """Initialize UI components for displaying and updating patient records."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Arial', sans-serif;
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
                border-radius: 10px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::horizontalHeader {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget::horizontalHeader::section {
                padding-left: 10px;
                padding-right: 10px;
                text-align: center;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e6fa7;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
           
        """)

        main_layout = QVBoxLayout()

        self.title_label = QLabel(f"Patient Record - ID: {self.patient_id}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0056b3;")
        main_layout.addWidget(self.title_label)

        # Create scrollable table
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow resizing

        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(14)
        self.patient_table.setHorizontalHeaderLabels([
            "ID", "Name", "Date of Birth", "Gender", "Contact Number",
            "Address", "Medical History", "Diagnosis", "Treatment Plan",
            "Prescription", "Lab Tests", "Radiography", "Notes", "Actions"
        ])

        # Enable word wrap for header labels
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
        self.patient_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.TextWordWrap)  # Enables text wrapping

        # Adjust row height dynamically for better readability
        self.patient_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # resize mode for column headers
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Set alternating row colors for readability
        self.patient_table.setAlternatingRowColors(True)

        # Set column width for "Actions" column
        self.patient_table.setColumnWidth(13, 350)

        # Enable scrolling
        self.patient_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patient_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Add table inside the scroll area
        self.scroll_area.setWidget(self.patient_table)
        main_layout.addWidget(self.scroll_area)

        
        self.setLayout(main_layout)
        self.load_assigned_patients()
    
    def load_assigned_patients(self):
        """Fetch and display patients Records to the doctor."""
        base_url = os.getenv("MEDICAL_RECORD_URL")
        api_url = f"{base_url}/{self.patient_id}"
        patient = fetch_data(self, api_url, self.token)

        if not patient:
            QMessageBox.information(self, "No Patients", "No patients have been assigned yet.")
            return

        # Set row count to 1 since it's a single patient
        self.patient_table.setRowCount(1)

        # Fill in patient details
        self.patient_table.setItem(0, 0, QTableWidgetItem(str(patient.get("id", ""))))
        self.patient_table.setItem(0, 1, QTableWidgetItem(patient.get("full_name", "")))
        self.patient_table.setItem(0, 2, QTableWidgetItem(patient.get("date_of_birth", "")))
        self.patient_table.setItem(0, 3, QTableWidgetItem(patient.get("gender", "")))
        self.patient_table.setItem(0, 4, QTableWidgetItem(patient.get("contact_number", "")))
        self.patient_table.setItem(0, 5, QTableWidgetItem(patient.get("address", "")))
        self.patient_table.setItem(0, 6, QTableWidgetItem(patient.get("medical_history", "")))
        self.patient_table.setItem(0, 7, QTableWidgetItem(patient.get("diagnosis", "")))
        self.patient_table.setItem(0, 8, QTableWidgetItem(patient.get("treatment_plan", "")))
        self.patient_table.setItem(0, 9, QTableWidgetItem(patient.get("prescription", "")))
        self.patient_table.setItem(0, 10, QTableWidgetItem(patient.get("lab_tests_results", "")))
        self.patient_table.setItem(0, 11, QTableWidgetItem(patient.get("scan_results", "")))
        self.patient_table.setItem(0, 12, QTableWidgetItem(patient.get("notes", "")))

        # Button to View Patient Record
        self.patient_table.setCellWidget(0, 13, self.create_view_button(patient.get("id", "")))


    def create_view_button(self, patient_id):
        """Create 'View Record' button for each patient."""
        button = QPushButton("Update Record")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.open_patient_record(patient_id))
        return button

    def open_patient_record(self, patient_id):
        """Open the patient record management window."""
        self.patient_record_window = PatientRecordUpdateWindow(patient_id)
        self.patient_record_window.show()
        
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