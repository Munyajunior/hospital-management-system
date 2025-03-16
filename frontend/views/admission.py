import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QTabWidget, QFormLayout, QLineEdit,
    QGridLayout, QGroupBox, QToolBar, QStatusBar, QMainWindow
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from utils.api_utils import fetch_data, post_data, update_data
from utils.pdf_utils import generate_pdf


class AdmissionManagement(QMainWindow):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the Admission Management interface.

        :param user_role: Role of the logged-in user (doctor/nurse/admin)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.role = user_role
        self.user_id = user_id
        self.token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admission Management System")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-size: 16px;
                color: #2c3e50;
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
                background-color: #1c5980;
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
            QTableWidget::horizontalHeader {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #dcdcdc;
                background-color: #f5f7fa;
            }
            QTabBar::tab {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2980b9;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 8px;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }
            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                margin-top: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)

        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Refresh Action
        refresh_action = QAction(QIcon("icons/refresh.png"), "Refresh", self)
        refresh_action.triggered.connect(self.refresh_all)
        self.toolbar.addAction(refresh_action)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Title
        self.title_label = QLabel("Admission Management System")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px; color: #2c3e50;")
        layout.addWidget(self.title_label)

        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Admission Tab
        self.admission_tab = QWidget()
        self.init_admission_tab()
        self.tabs.addTab(self.admission_tab, QIcon("icons/admit.png"), "Admit Patient")

        # Discharge Tab
        self.discharge_tab = QWidget()
        self.init_discharge_tab()
        self.tabs.addTab(self.discharge_tab, QIcon("icons/discharge.png"), "Discharge Patient")

        # ICU Management Tab
        self.icu_tab = QWidget()
        self.init_icu_tab()
        self.tabs.addTab(self.icu_tab, QIcon("icons/icu.png"), "ICU Management")

        # Inpatient Management Tab
        self.inpatient_tab = QWidget()
        self.init_inpatient_tab()
        self.tabs.addTab(self.inpatient_tab, QIcon("icons/inpatient.png"), "Inpatient Management")

        # Vitals Tab
        self.vitals_tab = QWidget()
        self.init_vitals_tab()
        self.tabs.addTab(self.vitals_tab, QIcon("icons/vitals.png"), "Update Vitals")

        # Department Management Tab
        self.department_tab = QWidget()
        self.init_department_tab()
        self.tabs.addTab(self.department_tab, QIcon("icons/department.png"), "Department Management")

        # Ward Management Tab
        self.ward_tab = QWidget()
        self.init_ward_tab()
        self.tabs.addTab(self.ward_tab, QIcon("icons/ward.png"), "Ward Management")

        # Bed Management Tab
        self.bed_tab = QWidget()
        self.init_bed_tab()
        self.tabs.addTab(self.bed_tab, QIcon("icons/bed.png"), "Bed Management")

    # ==================== Admission Tab ====================
    def init_admission_tab(self):
        layout = QVBoxLayout(self.admission_tab)

        # Admission Form
        form_group = QGroupBox("Admit Patient")
        form_layout = QFormLayout()

        self.patient_dropdown = QComboBox()
        self.load_patients()
        form_layout.addRow("Patient:", self.patient_dropdown)

        self.category_dropdown = QComboBox()
        self.category_dropdown.addItems(["Outpatient", "Inpatient", "ICU"])
        form_layout.addRow("Category:", self.category_dropdown)

        self.department_dropdown = QComboBox()
        self.department_dropdown.currentIndexChanged.connect(self.load_wards_for_department)
        self.load_departments()
        form_layout.addRow("Department:", self.department_dropdown)

        self.ward_dropdown = QComboBox()
        self.ward_dropdown.currentIndexChanged.connect(self.load_beds_for_ward)
        form_layout.addRow("Ward:", self.ward_dropdown)

        self.bed_dropdown = QComboBox()
        form_layout.addRow("Bed:", self.bed_dropdown)

        self.admit_button = QPushButton("Admit Patient")
        self.admit_button.setIcon(QIcon("icons/admit.png"))
        self.admit_button.setStyleSheet("background-color: #27ae60;")
        self.admit_button.clicked.connect(self.admit_patient)
        form_layout.addRow(self.admit_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

    # ==================== Discharge Tab ====================
    def init_discharge_tab(self):
        layout = QVBoxLayout(self.discharge_tab)

        # Discharge Form
        form_group = QGroupBox("Discharge Patient")
        form_layout = QFormLayout()

        self.admission_dropdown = QComboBox()
        self.load_admissions()
        form_layout.addRow("Admission:", self.admission_dropdown)

        self.discharge_button = QPushButton("Discharge Patient")
        self.discharge_button.setIcon(QIcon("icons/discharge.png"))
        self.discharge_button.setStyleSheet("background-color: #e74c3c;")
        self.discharge_button.clicked.connect(self.discharge_patient)
        form_layout.addRow(self.discharge_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

    # ==================== ICU Management Tab ====================
    def init_icu_tab(self):
        layout = QVBoxLayout(self.icu_tab)

        # ICU Patient Table
        table_group = QGroupBox("ICU Patients")
        table_layout = QVBoxLayout()

        self.icu_table = QTableWidget()
        self.icu_table.setColumnCount(8)
        self.icu_table.setHorizontalHeaderLabels([
            "Patient", "Status", "Condition Evolution", "Medications", "Drips", "Treatment Plan", "Updated By", "Updated At"
        ])
        table_layout.addWidget(self.icu_table)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("icons/refresh.png"))
        refresh_button.clicked.connect(self.load_icu_patients)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # ICU Patient Form
        form_group = QGroupBox("Update ICU Patient")
        form_layout = QFormLayout()

        self.patient_dropdown_icu = QComboBox()
        self.load_admitted_icu()
        form_layout.addRow("Patient:", self.patient_dropdown_icu)

        self.status_input_icu = QComboBox()
        self.status_input_icu.addItems(["Stable", "Critical", "Improving", "Deteriorating"])
        form_layout.addRow("Status:", self.status_input_icu)

        self.condition_evolution_input_icu = QTextEdit()
        self.condition_evolution_input_icu.setPlaceholderText("Enter condition evolution...")
        form_layout.addRow("Condition Evolution:", self.condition_evolution_input_icu)

        self.medications_input_icu = QTextEdit()
        self.medications_input_icu.setPlaceholderText("Enter medications...")
        form_layout.addRow("Medications:", self.medications_input_icu)

        self.drips_input_icu = QTextEdit()
        self.drips_input_icu.setPlaceholderText("Enter drips...")
        form_layout.addRow("Drips:", self.drips_input_icu)

        self.treatment_plan_input_icu = QTextEdit()
        self.treatment_plan_input_icu.setPlaceholderText("Enter treatment plan...")
        form_layout.addRow("Treatment Plan:", self.treatment_plan_input_icu)

        self.update_icu_button = QPushButton("Update ICU Patient")
        self.update_icu_button.setIcon(QIcon("icons/update.png"))
        self.update_icu_button.setStyleSheet("background-color: #007bff;")
        self.update_icu_button.clicked.connect(self.update_icu_patient)
        form_layout.addRow(self.update_icu_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

    # ==================== Inpatient Management Tab ====================
    def init_inpatient_tab(self):
        layout = QVBoxLayout(self.inpatient_tab)

        # Inpatient Table
        table_group = QGroupBox("Inpatients")
        table_layout = QVBoxLayout()

        self.inpatient_table = QTableWidget()
        self.inpatient_table.setColumnCount(7)
        self.inpatient_table.setHorizontalHeaderLabels([
            "Patient", "Status", "Condition Evolution", "Medications", "Treatment Plan", "Updated By", "Updated At"
        ])
        table_layout.addWidget(self.inpatient_table)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("icons/refresh.png"))
        refresh_button.clicked.connect(self.load_inpatients)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        # Inpatient Form
        form_group = QGroupBox("Update Inpatient")
        form_layout = QFormLayout()

        self.patient_dropdown_inpatient = QComboBox()
        self.load_admitted_inpatient()
        form_layout.addRow("Patient:", self.patient_dropdown_inpatient)

        self.status_input_inpatient = QComboBox()
        self.status_input_inpatient.addItems(["Stable", "Recovering", "Discharged"])
        form_layout.addRow("Status:", self.status_input_inpatient)

        self.condition_evolution_input_inpatient = QTextEdit()
        self.condition_evolution_input_inpatient.setPlaceholderText("Enter condition evolution...")
        form_layout.addRow("Condition Evolution:", self.condition_evolution_input_inpatient)

        self.medications_input_inpatient = QTextEdit()
        self.medications_input_inpatient.setPlaceholderText("Enter medications...")
        form_layout.addRow("Medications:", self.medications_input_inpatient)

        self.treatment_plan_input_inpatient = QTextEdit()
        self.treatment_plan_input_inpatient.setPlaceholderText("Enter treatment plan...")
        form_layout.addRow("Treatment Plan:", self.treatment_plan_input_inpatient)

        self.update_inpatient_button = QPushButton("Update Inpatient")
        self.update_inpatient_button.setIcon(QIcon("icons/update.png"))
        self.update_inpatient_button.setStyleSheet("background-color: #007bff;")
        self.update_inpatient_button.clicked.connect(self.update_inpatient)
        form_layout.addRow(self.update_inpatient_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

    # ==================== Vitals Tab ====================
    def init_vitals_tab(self):
        layout = QVBoxLayout(self.vitals_tab)

        # Vitals Form
        form_group = QGroupBox("Update Vitals")
        form_layout = QFormLayout()

        self.patient_dropdown_vitals = QComboBox()
        self.load_patients()
        form_layout.addRow("Patient:", self.patient_dropdown_vitals)

        self.blood_pressure_input = QLineEdit()
        self.blood_pressure_input.setPlaceholderText("Enter Blood Pressure...")
        form_layout.addRow("Blood Pressure:", self.blood_pressure_input)

        self.heart_rate_input = QLineEdit()
        self.heart_rate_input.setPlaceholderText("Enter Heart Rate...")
        form_layout.addRow("Heart Rate:", self.heart_rate_input)

        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("Enter Temperature...")
        form_layout.addRow("Temperature:", self.temperature_input)

        self.update_vitals_button = QPushButton("Update Vitals")
        self.update_vitals_button.setIcon(QIcon("icons/update.png"))
        self.update_vitals_button.setStyleSheet("background-color: #007bff;")
        self.update_vitals_button.clicked.connect(self.update_vitals)
        form_layout.addRow(self.update_vitals_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

    # ==================== Department Management Tab ====================
    def init_department_tab(self):
        layout = QVBoxLayout(self.department_tab)

        # Department Creation Form
        form_group = QGroupBox("Create Department")
        form_layout = QFormLayout()

        self.department_name_input = QLineEdit()
        self.department_name_input.setPlaceholderText("Enter Department Name")
        form_layout.addRow("Department Name:", self.department_name_input)

        self.department_category_dropdown = QComboBox()
        self.department_category_dropdown.addItems(["Outpatient", "Inpatient", "ICU"])
        form_layout.addRow("Category:", self.department_category_dropdown)

        self.create_department_button = QPushButton("Create Department")
        self.create_department_button.setIcon(QIcon("icons/create.png"))
        self.create_department_button.setStyleSheet("background-color: #007bff;")
        self.create_department_button.clicked.connect(self.create_department)
        form_layout.addRow(self.create_department_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Department Table
        table_group = QGroupBox("Existing Departments")
        table_layout = QVBoxLayout()

        self.existing_department_table = QTableWidget()
        self.existing_department_table.setColumnCount(3)
        self.existing_department_table.setHorizontalHeaderLabels(["ID", "Name", "Category"])
        table_layout.addWidget(self.existing_department_table)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("icons/refresh.png"))
        refresh_button.clicked.connect(self.load_existing_departments)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    # ==================== Ward Management Tab ====================
    def init_ward_tab(self):
        layout = QVBoxLayout(self.ward_tab)

        # Ward Creation Form
        form_group = QGroupBox("Create Ward")
        form_layout = QFormLayout()

        self.ward_name_input = QLineEdit()
        self.ward_name_input.setPlaceholderText("Enter Ward Name")
        form_layout.addRow("Ward Name:", self.ward_name_input)

        self.department_dropdown_ward = QComboBox()
        self.load_departments_for_ward()
        form_layout.addRow("Department:", self.department_dropdown_ward)

        self.create_ward_button = QPushButton("Create Ward")
        self.create_ward_button.setIcon(QIcon("icons/create.png"))
        self.create_ward_button.setStyleSheet("background-color: #007bff;")
        self.create_ward_button.clicked.connect(self.create_ward)
        form_layout.addRow(self.create_ward_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Ward Table
        table_group = QGroupBox("Existing Wards")
        table_layout = QVBoxLayout()

        self.ward_table = QTableWidget()
        self.ward_table.setColumnCount(3)
        self.ward_table.setHorizontalHeaderLabels(["ID", "Name", "Department"])
        table_layout.addWidget(self.ward_table)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("icons/refresh.png"))
        refresh_button.clicked.connect(self.load_wards)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    # ==================== Bed Management Tab ====================
    def init_bed_tab(self):
        layout = QVBoxLayout(self.bed_tab)

        # Bed Creation Form
        form_group = QGroupBox("Create Bed")
        form_layout = QFormLayout()

        self.bed_number_input = QLineEdit()
        self.bed_number_input.setPlaceholderText("Enter Bed Number")
        form_layout.addRow("Bed Number:", self.bed_number_input)

        self.ward_dropdown_bed = QComboBox()
        self.load_wards_for_bed()
        form_layout.addRow("Ward:", self.ward_dropdown_bed)

        self.create_bed_button = QPushButton("Create Bed")
        self.create_bed_button.setIcon(QIcon("icons/create.png"))
        self.create_bed_button.setStyleSheet("background-color: #007bff;")
        self.create_bed_button.clicked.connect(self.create_bed)
        form_layout.addRow(self.create_bed_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Bed Table
        table_group = QGroupBox("Existing Beds")
        table_layout = QVBoxLayout()

        self.bed_table = QTableWidget()
        self.bed_table.setColumnCount(3)
        self.bed_table.setHorizontalHeaderLabels(["ID", "Bed Number", "Ward"])
        table_layout.addWidget(self.bed_table)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("icons/refresh.png"))
        refresh_button.clicked.connect(self.load_beds)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

    # ==================== Helper Methods ====================
    def load_patients(self):
        """Fetches and populates the dropdown with patients."""
        api_url = os.getenv("PATIENT_LIST_URL")
        patients = fetch_data(self, api_url, self.token)

        if patients:
            self.patient_dropdown.clear()
            self.patient_dropdown_vitals.clear()
            for patient in patients:
                self.patient_dropdown.addItem(patient["full_name"], patient["id"])
                self.patient_dropdown_vitals.addItem(patient["full_name"], patient["id"])

    def load_admissions(self):
        """Fetches and populates the dropdown with admissions."""
        api_url = os.getenv("ADMISSION_LIST_URL")
        admissions = fetch_data(self, api_url, self.token)

        if admissions:
            self.admission_dropdown.clear()
            for admission in admissions:
                self.admission_dropdown.addItem(f"Admission {admission['id']}", admission["id"])
                
    def load_admitted_icu(self):
        """Fetches and populates the dropdown with admissions."""
        api_url = os.getenv("GET_ICU_PATIENTS_URL")
        admissions = fetch_data(self, api_url, self.token)

        if admissions:
            self.patient_dropdown_icu.clear()
            for admission in admissions:
                self.patient_dropdown_icu.addItem(f"Admission {admission['id']}", admission["id"])


    def load_icu_patients(self):
        """Fetches and displays ICU patients."""
        api_url = os.getenv("GET_ICU_PATIENTS_URL")
        icu_patients = fetch_data(self, api_url, self.token)

        if icu_patients:
            self.icu_table.setRowCount(len(icu_patients))
            for row, patient in enumerate(icu_patients):
                self.icu_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
                self.icu_table.setItem(row, 1, QTableWidgetItem(patient["status"]))
                self.icu_table.setItem(row, 2, QTableWidgetItem(patient["condition_evolution"]))
                self.icu_table.setItem(row, 3, QTableWidgetItem(patient["medications"]))
                self.icu_table.setItem(row, 4, QTableWidgetItem(patient["drips"]))
                self.icu_table.setItem(row, 5, QTableWidgetItem(patient["treatment_plan"]))
                self.icu_table.setItem(row, 6, QTableWidgetItem(patient["updated_by"]))
                self.icu_table.setItem(row, 7, QTableWidgetItem(patient["updated_at"]))

    
    def load_admitted_inpatient(self):
        """Fetches and populates the dropdown with Inpatient admissions."""
        api_url = os.getenv("GET_INPATIENTS_URL")
        in_patient = fetch_data(self, api_url, self.token)
        
        if in_patient:
            for patient in in_patient:
                self.patient_dropdown_inpatient.addItem(f"Admission {patient['id']}", patient["id"])
                
    def load_inpatients(self):
        """Fetches and displays inpatients."""
        api_url = os.getenv("GET_INPATIENTS_URL")
        inpatients = fetch_data(self, api_url, self.token)

        if inpatients:
            self.inpatient_table.setRowCount(len(inpatients))
            for row, patient in enumerate(inpatients):
                self.inpatient_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
                self.inpatient_table.setItem(row, 1, QTableWidgetItem(patient["status"]))
                self.inpatient_table.setItem(row, 2, QTableWidgetItem(patient["condition_evolution"]))
                self.inpatient_table.setItem(row, 3, QTableWidgetItem(patient["medications"]))
                self.inpatient_table.setItem(row, 4, QTableWidgetItem(patient["treatment_plan"]))
                self.inpatient_table.setItem(row, 5, QTableWidgetItem(patient["updated_by"]))
                self.inpatient_table.setItem(row, 6, QTableWidgetItem(patient["updated_at"]))

    def load_departments(self):
        """Fetches and populates the dropdown with departments."""
        api_url = os.getenv("DEPARTMENT_LIST_URL")
        departments = fetch_data(self, api_url, self.token)

        if departments:
            self.department_dropdown.clear()
            for department in departments:
                self.department_dropdown.addItem(department["name"], department["id"])

    def load_wards_for_department(self):
        """Fetches and populates the dropdown with wards for a selected department."""
        department_id = self.department_dropdown.currentData()
        if department_id:
            api_url = os.getenv("WARD_LIST_URL") + f"?department_id={department_id}"
            wards = fetch_data(self, api_url, self.token)
            self.ward_dropdown.clear()
            for ward in wards:
                self.ward_dropdown.addItem(ward["name"], ward["id"])

    def load_beds_for_ward(self):
        """Fetches and populates the dropdown with beds for a selected ward."""
        ward_id = self.ward_dropdown.currentData()
        if ward_id:
            api_url = os.getenv("BED_LIST_URL") + f"?ward_id={ward_id}&is_occupied=False"
            beds = fetch_data(self, api_url, self.token)
            self.bed_dropdown.clear()
            for bed in beds:
                self.bed_dropdown.addItem(bed["bed_number"], bed["id"])

    def load_departments_for_ward(self):
        """Fetches and populates the dropdown with departments for ward creation."""
        api_url = os.getenv("DEPARTMENT_LIST_URL")
        departments = fetch_data(self, api_url, self.token)

        if departments:
            self.department_dropdown_ward.clear()
            for department in departments:
                self.department_dropdown_ward.addItem(department["name"], department["id"])

    def load_wards_for_bed(self):
        """Fetches and populates the dropdown with wards for bed creation."""
        api_url = os.getenv("WARD_LIST_URL")
        wards = fetch_data(self, api_url, self.token)

        if wards:
            self.ward_dropdown_bed.clear()
            for ward in wards:
                self.ward_dropdown_bed.addItem(ward["name"], ward["id"])

    def load_existing_departments(self):
        """Fetches and displays existing departments."""
        api_url = os.getenv("DEPARTMENT_LIST_URL")
        departments = fetch_data(self, api_url, self.token)

        if departments:
            self.existing_department_table.setRowCount(len(departments))
            for row, department in enumerate(departments):
                self.existing_department_table.setItem(row, 0, QTableWidgetItem(str(department["id"])))
                self.existing_department_table.setItem(row, 1, QTableWidgetItem(department["name"]))
                self.existing_department_table.setItem(row, 2, QTableWidgetItem(department["category"]))

    def load_wards(self):
        """Fetches and displays existing wards."""
        api_url = os.getenv("WARD_LIST_URL")
        wards = fetch_data(self, api_url, self.token)

        if wards:
            self.ward_table.setRowCount(len(wards))
            for row, ward in enumerate(wards):
                self.ward_table.setItem(row, 0, QTableWidgetItem(str(ward["id"])))
                self.ward_table.setItem(row, 1, QTableWidgetItem(ward["name"]))
                self.ward_table.setItem(row, 2, QTableWidgetItem(ward["department_name"]))

    def load_beds(self):
        """Fetches and displays existing beds."""
        api_url = os.getenv("BED_LIST_URL")
        beds = fetch_data(self, api_url, self.token)

        if beds:
            self.bed_table.setRowCount(len(beds))
            for row, bed in enumerate(beds):
                self.bed_table.setItem(row, 0, QTableWidgetItem(str(bed["id"])))
                self.bed_table.setItem(row, 1, QTableWidgetItem(bed["bed_number"]))
                self.bed_table.setItem(row, 2, QTableWidgetItem(bed["ward_name"]))

    # ==================== API Interaction Methods ====================
    def admit_patient(self):
        """Admits a patient."""
        patient_id = self.patient_dropdown.currentData()
        category = self.category_dropdown.currentText()
        department_id = self.department_dropdown.currentData()
        ward_id = self.ward_dropdown.currentData()
        bed_id = self.bed_dropdown.currentData()

        if not patient_id or not category or not department_id or not ward_id or not bed_id:
            QMessageBox.warning(self, "Validation Error", "Please fill all fields.")
            return

        api_url = os.getenv("ADMIT_PATIENT_URL")
        data = {
            "patient_id": patient_id,
            "category": category,
            "department_id": department_id,
            "ward_id": ward_id,
            "bed_id": bed_id
        }
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Patient admitted successfully.")
            self.load_admissions()
        else:
            QMessageBox.critical(self, "Error", "Failed to admit patient.")

    def discharge_patient(self):
        """Discharges a patient."""
        admission_id = self.admission_dropdown.currentData()

        if not admission_id:
            QMessageBox.warning(self, "Validation Error", "Please select an admission.")
            return

        base_url = os.getenv("DISCHARGE_PATIENT_URL")
        api_url = f"{base_url}{admission_id}/discharge"
        response = update_data(self, api_url, {"admission_id": admission_id}, self.token)

        if response:
            QMessageBox.information(self, "Success", "Patient discharged successfully.")
            self.load_admissions()
        else:
            QMessageBox.critical(self, "Error", "Failed to discharge patient.")

    def update_icu_patient(self):
        """Updates ICU patient details."""
        patient_id = self.patient_dropdown_icu.currentData()
        status = self.status_input_icu.currentText()
        condition_evolution = self.condition_evolution_input_icu.toPlainText()
        medications = self.medications_input_icu.toPlainText()
        drips = self.drips_input_icu.toPlainText()
        treatment_plan = self.treatment_plan_input_icu.toPlainText()

        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient.")
            return

        base_url = os.getenv("UPDATE_ICU_PATIENT_URL")
        api_url = f"{base_url}{patient_id}"
        data = {
            "patient_id": patient_id,
            "status": status,
            "condition_evolution": condition_evolution,
            "medications": medications,
            "drips": drips,
            "treatment_plan": treatment_plan
        }
        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "ICU patient updated successfully.")
            self.load_icu_patients()
        else:
            QMessageBox.critical(self, "Error", "Failed to update ICU patient.")

    def update_inpatient(self):
        """Updates inpatient details."""
        patient_id = self.patient_dropdown_inpatient.currentData()
        status = self.status_input_inpatient.currentText()
        condition_evolution = self.condition_evolution_input_inpatient.toPlainText()
        medications = self.medications_input_inpatient.toPlainText()
        treatment_plan = self.treatment_plan_input_inpatient.toPlainText()

        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient.")
            return

        base_url = os.getenv("UPDATE_INPATIENT_URL")
        api_url = f"{base_url}{patient_id}"
        data = {
            "patient_id": patient_id,
            "status": status,
            "condition_evolution": condition_evolution,
            "medications": medications,
            "treatment_plan": treatment_plan
        }
        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Inpatient updated successfully.")
            self.load_inpatients()
        else:
            QMessageBox.critical(self, "Error", "Failed to update inpatient.")

    def update_vitals(self):
        """Updates patient vitals."""
        patient_id = self.patient_dropdown_vitals.currentData()
        blood_pressure = self.blood_pressure_input.text()
        heart_rate = self.heart_rate_input.text()
        temperature = self.temperature_input.text()

        if not patient_id or not blood_pressure or not heart_rate or not temperature:
            QMessageBox.warning(self, "Validation Error", "Please fill all fields.")
            return

        api_url = os.getenv("UPDATE_VITALS_URL")
        data = {
            "patient_id": patient_id,
            "blood_pressure": blood_pressure,
            "heart_rate": heart_rate,
            "temperature": temperature,
            "updated_by": self.user_id
        }
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Vitals updated successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to update vitals.")

    def create_department(self):
        """Creates a new department."""
        name = self.department_name_input.text().strip()
        category = self.department_category_dropdown.currentText()

        if not name or not category:
            QMessageBox.warning(self, "Validation Error", "Please fill all fields.")
            return

        api_url = os.getenv("CREATE_DEPARTMENT_URL")
        data = {
            "name": name,
            "category": category
        }
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Department created successfully.")
            self.load_existing_departments()
        else:
            QMessageBox.critical(self, "Error", "Failed to create department.")

    def create_ward(self):
        """Creates a new ward."""
        name = self.ward_name_input.text().strip()
        department_id = self.department_dropdown_ward.currentData()

        if not name or not department_id:
            QMessageBox.warning(self, "Validation Error", "Please fill all fields.")
            return

        api_url = os.getenv("CREATE_WARD_URL")
        data = {
            "name": name,
            "department_id": department_id
        }
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Ward created successfully.")
            self.load_wards()
        else:
            QMessageBox.critical(self, "Error", "Failed to create ward.")

    def create_bed(self):
        """Creates a new bed."""
        bed_number = self.bed_number_input.text().strip()
        ward_id = self.ward_dropdown_bed.currentData()

        if not bed_number or not ward_id:
            QMessageBox.warning(self, "Validation Error", "Please fill all fields.")
            return

        api_url = os.getenv("CREATE_BED_URL")
        data = {
            "bed_number": bed_number,
            "ward_id": ward_id
        }
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Bed created successfully.")
            self.load_beds()
        else:
            QMessageBox.critical(self, "Error", "Failed to create bed.")

    def refresh_all(self):
        """Refreshes all tabs."""
        self.load_patients()
        self.load_admissions()
        self.load_icu_patients()
        self.load_inpatients()
        self.load_existing_departments()
        self.load_wards()
        self.load_beds()
        self.status_bar.showMessage("All data refreshed successfully.", 3000)