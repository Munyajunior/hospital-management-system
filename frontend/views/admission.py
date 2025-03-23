import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QTabWidget, QFormLayout, QLineEdit, QGridLayout,
    QGroupBox, QToolBar, QStatusBar, QMainWindow, QScrollArea, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction, QFont
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
        self.is_dark_theme = False  # Track theme state
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admission Management System")
        # Dynamically set window size based on screen resolution
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height

        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(800, 600)  # Set a reasonable minimum size

        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Refresh Action
        refresh_action = QAction(QIcon("assets/icons/refresh.png"), "Refresh", self)
        refresh_action.triggered.connect(self.refresh_all)
        self.toolbar.addAction(refresh_action)

        # Theme Toggle Action
        self.toggle_theme_action = QAction(QIcon("assets/icons/theme.png"), "Toggle Theme", self)
        self.toggle_theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.toggle_theme_action)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Title
        self.title_label = QLabel("Admission Management System")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(self.title_label)

        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Initialize dropdowns globally
        self.patient_dropdown = QComboBox()
        self.patient_dropdown_vitals = QComboBox()
        self.bed_dropdown = QComboBox()
        self.ward_dropdown = QComboBox()

        # Admission Tab
        self.admission_tab = QWidget()
        self.init_admission_tab()
        self.tabs.addTab(self.admission_tab, QIcon("assets/icons/admit.png"), "Admit Patient")

        # Discharge Tab
        self.discharge_tab = QWidget()
        self.init_discharge_tab()
        self.tabs.addTab(self.discharge_tab, QIcon("assets/icons/discharge.png"), "Discharge Patient")

        # ICU Management Tab
        self.icu_tab = QWidget()
        self.init_icu_tab()
        self.tabs.addTab(self.icu_tab, QIcon("assets/icons/icu.png"), "ICU Management")

        # Inpatient Management Tab
        self.inpatient_tab = QWidget()
        self.init_inpatient_tab()
        self.tabs.addTab(self.inpatient_tab, QIcon("assets/icons/inpatient.png"), "Inpatient Management")

        # Vitals Tab
        self.vitals_tab = QWidget()
        self.init_vitals_tab()
        self.tabs.addTab(self.vitals_tab, QIcon("assets/icons/vitals.png"), "Update Vitals")

        # Department Management Tab
        self.department_tab = QWidget()
        self.init_department_tab()
        self.tabs.addTab(self.department_tab, QIcon("assets/icons/department.png"), "Department Management")

        # Ward Management Tab
        self.ward_tab = QWidget()
        self.init_ward_tab()
        self.tabs.addTab(self.ward_tab, QIcon("assets/icons/ward.png"), "Ward Management")

        # Bed Management Tab
        self.bed_tab = QWidget()
        self.init_bed_tab()
        self.tabs.addTab(self.bed_tab, QIcon("assets/icons/bed.png"), "Bed Management")

        # Apply the initial theme
        self.apply_theme()

    def toggle_theme(self):
        """Toggles between light and dark themes."""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        """Applies the current theme (light or dark)."""
        if self.is_dark_theme:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2C3E50;
                    color: #ECF0F1;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 14px;
                }
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #ECF0F1;
                }
                QTableWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    alternate-background-color: #2C3E50;
                    font-size: 14px;
                }
                QHeaderView::section {
                    background-color: #007BFF;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                QLineEdit, QComboBox, QTextEdit, QListWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    border: 1px solid #5D6D7E;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.toggle_theme_action.setText("☀️ Light Theme")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F4F6F7;
                    color: #2C3E50;
                    font-family: 'Segoe UI', 'Arial', sans-serif;
                    font-size: 14px;
                }
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2C3E50;
                }
                QTableWidget {
                    background-color: white;
                    color: #2C3E50;
                    alternate-background-color: #F8F9F9;
                    font-size: 14px;
                }
                QHeaderView::section {
                    background-color: #007BFF;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                QLineEdit, QComboBox, QTextEdit, QListWidget {
                    background-color: white;
                    color: #2C3E50;
                    border: 1px solid #D5DBDB;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.toggle_theme_action.setText("🌙 Dark Theme")

    # ==================== Admission Tab ====================
    def init_admission_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)
        
        # Admitted Patient Table
        table_group = QGroupBox("Admitted Patients")
        table_layout = QVBoxLayout()

        self.admitted_table = QTableWidget()
        self.admitted_table.setColumnCount(9)
        self.admitted_table.setHorizontalHeaderLabels([
            "Patient", "Admitted by", "Assigned Doctor", "Category", "Department", "Ward", "Bed", "Status",
            "Admission Date"
        ])
         # Set size policy to ensure the table expands
        self.admitted_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set a minimum height to accommodate at least 10 rows
        self.admitted_table.setMinimumHeight(300)
        self.admitted_table.horizontalHeader().setStretchLastSection(True)
        self.admitted_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.admitted_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.admitted_table, stretch=1)
        
        # Add duplicate header at the top
        self.admitted_table.setRowCount(self.admitted_table.rowCount() + 1)
        for col in range(self.admitted_table.columnCount()):
            item = QTableWidgetItem(self.admitted_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.admitted_table.setItem(self.admitted_table.rowCount() - 1, col, item)
        
        self.load_admitted_patient()

        # Search Bar
        self.admitted_search_input = QLineEdit()
        self.admitted_search_input.setPlaceholderText("Search Admitted Patients...")
        self.admitted_search_input.textChanged.connect(self.filter_admitted_patients)
        table_layout.addWidget(self.admitted_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        refresh_button.clicked.connect(self.load_admitted_patient)
        table_layout.addWidget(refresh_button)
        
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
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
        self.load_wards()
        form_layout.addRow("Ward:", self.ward_dropdown)

        self.bed_dropdown = QComboBox()
        self.load_beds()
        form_layout.addRow("Bed:", self.bed_dropdown)

        self.admit_button = QPushButton("Admit Patient")
        self.admit_button.setIcon(QIcon("assets/icons/admit.png"))
        self.admit_button.setStyleSheet("background-color: #27ae60;")
        self.admit_button.clicked.connect(self.admit_patient)
        form_layout.addRow(self.admit_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        self.admission_tab.setLayout(QVBoxLayout())
        self.admission_tab.layout().addWidget(scroll_area)

    # ==================== Discharge Tab ====================
    def init_discharge_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)

        # Discharge Form
        form_group = QGroupBox("Discharge Patient")
        form_layout = QFormLayout()

        self.admission_dropdown = QComboBox()
        self.load_admissions()
        form_layout.addRow("Admission:", self.admission_dropdown)

        self.discharge_button = QPushButton("Discharge Patient")
        self.discharge_button.setIcon(QIcon("assets/icons/discharge.png"))
        self.discharge_button.setStyleSheet("background-color: #e74c3c;")
        self.discharge_button.clicked.connect(self.discharge_patient)
        form_layout.addRow(self.discharge_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        self.discharge_tab.setLayout(QVBoxLayout())
        self.discharge_tab.layout().addWidget(scroll_area)

    # ==================== ICU Management Tab ====================
    def init_icu_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)

        # ICU Patient Table
        table_group = QGroupBox("ICU Patients")
        table_layout = QVBoxLayout()

        self.icu_table = QTableWidget()
        self.icu_table.setColumnCount(8)
        self.icu_table.setHorizontalHeaderLabels([
            "Patient", "Status", "Condition Evolution", "Medications", "Drips", "Treatment Plan", "Updated By", "Updated At"
        ])
        self.icu_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icu_table.setMinimumHeight(200)
        self.icu_table.horizontalHeader().setStretchLastSection(True)
        self.icu_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.icu_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.icu_table, stretch=1)

        # Add duplicate header at the top
        self.icu_table.insertRow(0)
        for col in range(self.icu_table.columnCount()):
            item = QTableWidgetItem(self.icu_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.icu_table.setItem(0, col, item)

        # Search Bar
        self.icu_search_input = QLineEdit()
        self.icu_search_input.setPlaceholderText("Search ICU Patients...")
        self.icu_search_input.textChanged.connect(self.filter_icu_patients)
        table_layout.addWidget(self.icu_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
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
        self.update_icu_button.setIcon(QIcon("assets/icons/update.png"))
        self.update_icu_button.setStyleSheet("background-color: #007bff;")
        self.update_icu_button.clicked.connect(self.update_icu_patient)
        form_layout.addRow(self.update_icu_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        self.icu_tab.setLayout(QVBoxLayout())
        self.icu_tab.layout().addWidget(scroll_area)

    # ==================== Inpatient Management Tab ====================
    def init_inpatient_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)

        # Inpatient Table
        table_group = QGroupBox("Inpatients")
        table_layout = QVBoxLayout()

        self.inpatient_table = QTableWidget()
        self.inpatient_table.setColumnCount(7)
        self.inpatient_table.setHorizontalHeaderLabels([
            "Patient", "Status", "Condition Evolution", "Medications", "Treatment Plan", "Updated By", "Updated At"
        ])
        self.inpatient_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.inpatient_table.setMinimumHeight(200)
        self.inpatient_table.horizontalHeader().setStretchLastSection(True)
        self.inpatient_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.inpatient_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.inpatient_table)

        # Add duplicate header at the top
        self.inpatient_table.insertRow(0)
        for col in range(self.inpatient_table.columnCount()):
            item = QTableWidgetItem(self.inpatient_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.inpatient_table.setItem(0, col, item)

        # Search Bar
        self.inpatient_search_input = QLineEdit()
        self.inpatient_search_input.setPlaceholderText("Search Inpatients...")
        self.inpatient_search_input.textChanged.connect(self.filter_inpatients)
        table_layout.addWidget(self.inpatient_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
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
        self.update_inpatient_button.setIcon(QIcon("assets/icons/update.png"))
        self.update_inpatient_button.setStyleSheet("background-color: #007bff;")
        self.update_inpatient_button.clicked.connect(self.update_inpatient)
        form_layout.addRow(self.update_inpatient_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        self.inpatient_tab.setLayout(QVBoxLayout())
        self.inpatient_tab.layout().addWidget(scroll_area)

    # ==================== Vitals Tab ====================
    def init_vitals_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)
        
        # VItals Table
        table_group = QGroupBox("Patients Vitals")
        table_layout = QVBoxLayout()

        self.vital_table = QTableWidget()
        self.vital_table.setColumnCount(6)
        self.vital_table.setHorizontalHeaderLabels([
            "Patient", "Blood Pressure", "Heart Rate", "Temperature", "Updated By", "Updated At"
        ])
        self.vital_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vital_table.setMinimumHeight(200)
        self.vital_table.horizontalHeader().setStretchLastSection(True)
        self.vital_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vital_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.vital_table)

        # Add duplicate header at the top
        self.vital_table.insertRow(0)
        for col in range(self.vital_table.columnCount()):
            item = QTableWidgetItem(self.vital_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.vital_table.setItem(0, col, item)

        # Search Bar
        self.vital_search_input = QLineEdit()
        self.vital_search_input.setPlaceholderText("Search Vitals...")
        self.vital_search_input.textChanged.connect(self.filter_vitals)
        table_layout.addWidget(self.vital_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        refresh_button.clicked.connect(self.load_vitals)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        
        self.load_vitals()
        # Vitals Form
        form_group = QGroupBox("Update Vitals")
        form_layout = QFormLayout()

        self.patient_dropdown_vitals = QComboBox()
        self.load_admissions()
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
        self.update_vitals_button.setIcon(QIcon("assets/icons/update.png"))
        self.update_vitals_button.setStyleSheet("background-color: #007bff;")
        self.update_vitals_button.clicked.connect(self.update_vitals)
        form_layout.addRow(self.update_vitals_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Anomaly Detection Section
        anomaly_group = QGroupBox("Anomaly Detection")
        anomaly_layout = QVBoxLayout()

        self.anomalies_label = QLabel("Anomalies Detected:")
        self.anomalies_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.anomalies_label.setStyleSheet("color: #2c3e50;")
        anomaly_layout.addWidget(self.anomalies_label)

        self.anomalies_text = QLabel("No anomalies detected.")
        self.anomalies_text.setFont(QFont("Segoe UI", 12))
        self.anomalies_text.setStyleSheet("color: #333333;")
        anomaly_layout.addWidget(self.anomalies_text)

        anomaly_group.setLayout(anomaly_layout)
        layout.addWidget(anomaly_group)

        self.vitals_tab.setLayout(QVBoxLayout())
        self.vitals_tab.layout().addWidget(scroll_area)

    # ==================== Department Management Tab ====================
    def init_department_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)

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
        self.create_department_button.setIcon(QIcon("assets/icons/create.png"))
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
        self.existing_department_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.existing_department_table.setMinimumHeight(200)
        self.existing_department_table.horizontalHeader().setStretchLastSection(True)
        self.existing_department_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.existing_department_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.existing_department_table)

        # Add duplicate header at the top
        self.existing_department_table.insertRow(0)
        for col in range(self.existing_department_table.columnCount()):
            item = QTableWidgetItem(self.existing_department_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.existing_department_table.setItem(0, col, item)

        # Search Bar
        self.department_search_input = QLineEdit()
        self.department_search_input.setPlaceholderText("Search Departments...")
        self.department_search_input.textChanged.connect(self.filter_departments)
        table_layout.addWidget(self.department_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        refresh_button.clicked.connect(self.load_existing_departments)
        table_layout.addWidget(refresh_button)

        self.load_existing_departments()
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        self.department_tab.setLayout(QVBoxLayout())
        self.department_tab.layout().addWidget(scroll_area)

    # ==================== Ward Management Tab ====================
    def init_ward_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)

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
        self.create_ward_button.setIcon(QIcon("assets/icons/create.png"))
        self.create_ward_button.setStyleSheet("background-color: #007bff;")
        self.create_ward_button.clicked.connect(self.create_ward)
        form_layout.addRow(self.create_ward_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Ward Table
        table_group = QGroupBox("Existing Wards")
        table_layout = QVBoxLayout()

        self.existing_ward_table = QTableWidget()
        self.existing_ward_table.setColumnCount(3)
        self.existing_ward_table.setHorizontalHeaderLabels(["ID", "Name", "Department"])
        self.existing_ward_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.existing_ward_table.setMinimumHeight(200)
        self.existing_ward_table.horizontalHeader().setStretchLastSection(True)
        self.existing_ward_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.existing_ward_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.existing_ward_table)

        # Add duplicate header at the top
        self.existing_ward_table.insertRow(0)
        for col in range(self.existing_ward_table.columnCount()):
            item = QTableWidgetItem(self.existing_ward_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.existing_ward_table.setItem(0, col, item)

        # Search Bar
        self.ward_search_input = QLineEdit()
        self.ward_search_input.setPlaceholderText("Search Wards...")
        self.ward_search_input.textChanged.connect(self.filter_wards)
        table_layout.addWidget(self.ward_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        refresh_button.clicked.connect(self.load_existing_wards)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        self.load_existing_wards()
        
        self.ward_tab.setLayout(QVBoxLayout())
        self.ward_tab.layout().addWidget(scroll_area)

    # ==================== Bed Management Tab ====================
    def init_bed_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        layout = QVBoxLayout(scroll_widget)

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
        self.create_bed_button.setIcon(QIcon("assets/icons/create.png"))
        self.create_bed_button.setStyleSheet("background-color: #007bff;")
        self.create_bed_button.clicked.connect(self.create_bed)
        form_layout.addRow(self.create_bed_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Bed Table
        table_group = QGroupBox("Existing Beds")
        table_layout = QVBoxLayout()

        self.existing_bed_table = QTableWidget()
        self.existing_bed_table.setColumnCount(3)
        self.existing_bed_table.setHorizontalHeaderLabels(["ID", "Bed Number", "Ward"])
        self.existing_bed_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.existing_bed_table.setMinimumHeight(200)
        self.existing_bed_table.horizontalHeader().setStretchLastSection(True)
        self.existing_bed_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.existing_bed_table.horizontalHeader().setTextElideMode(Qt.ElideRight)
        table_layout.addWidget(self.existing_bed_table)

        # Add duplicate header at the top
        self.existing_bed_table.insertRow(0)
        for col in range(self.existing_bed_table.columnCount()):
            item = QTableWidgetItem(self.existing_bed_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.existing_bed_table.setItem(0, col, item)

        # Search Bar
        self.bed_search_input = QLineEdit()
        self.bed_search_input.setPlaceholderText("Search Beds...")
        self.bed_search_input.textChanged.connect(self.filter_beds)
        table_layout.addWidget(self.bed_search_input)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("assets/icons/refresh.png"))
        refresh_button.clicked.connect(self.load_existing_beds)
        table_layout.addWidget(refresh_button)

        table_group.setLayout(table_layout)
        layout.addWidget(table_group)

        self.load_existing_beds()
        
        self.bed_tab.setLayout(QVBoxLayout())
        self.bed_tab.layout().addWidget(scroll_area)

    # ==================== Search Functionality ====================
    def filter_admitted_patients(self):
        """Filter Admitted patients based on search"""
        search_text = self.admitted_search_input.text().lower()
        for row in range(self.admitted_table.rowCount()):
            match = False
            for col in range(self.admitted_table.columnCount()):
                item = self.admitted_table.item(row, col)
                if item and search_text in item.text().low():
                    match = True
                    break
                self.admitted_table.setRowHidden(row, not match)
    
    def filter_icu_patients(self):
        """Filters ICU patients based on search input."""
        search_text = self.icu_search_input.text().lower()
        for row in range(self.icu_table.rowCount()):
            match = False
            for col in range(self.icu_table.columnCount()):
                item = self.icu_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.icu_table.setRowHidden(row, not match)

    def filter_inpatients(self):
        """Filters inpatients based on search input."""
        search_text = self.inpatient_search_input.text().lower()
        for row in range(self.inpatient_table.rowCount()):
            match = False
            for col in range(self.inpatient_table.columnCount()):
                item = self.inpatient_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.inpatient_table.setRowHidden(row, not match)
    def filter_vitals(self):
        """Filters the vitals table based on the search input."""
        search_text = self.vital_search_input.text().strip().lower()

        for row in range(self.vital_table.rowCount()):
            match = False
            for col in range(self.vital_table.columnCount()):
                item = self.vital_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.vital_table.setRowHidden(row, not match)
    def filter_departments(self):
        """Filters departments based on search input."""
        search_text = self.department_search_input.text().lower()
        for row in range(self.existing_department_table.rowCount()):
            match = False
            for col in range(self.existing_department_table.columnCount()):
                item = self.existing_department_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.existing_department_table.setRowHidden(row, not match)

    def filter_wards(self):
        """Filters wards based on search input."""
        search_text = self.ward_search_input.text().lower()
        for row in range(self.existing_ward_table.rowCount()):
            match = False
            for col in range(self.existing_ward_table.columnCount()):
                item = self.existing_ward_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.existing_ward_table.setRowHidden(row, not match)

    def filter_beds(self):
        """Filters beds based on search input."""
        search_text = self.bed_search_input.text().lower()
        for row in range(self.existing_bed_table.rowCount()):
            match = False
            for col in range(self.existing_bed_table.columnCount()):
                item = self.existing_bed_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.existing_bed_table.setRowHidden(row, not match)

    # ==================== Threading for API Calls ====================
    def load_patients(self):
        """Fetches and populates the dropdown with patients using threading."""
        try:
            patients = fetch_data(self, os.getenv("PATIENT_LIST_URL")+ "?emergency=false", self.token)
            self.populate_patient_dropdowns(patients)
        except Exception as e:
            self.show_error(str(e))

    def populate_patient_dropdowns(self, patients):
        """Populates patient dropdowns with fetched data."""
        if patients:
            self.patient_dropdown.clear()
            for patient in patients:
                self.patient_dropdown.addItem(patient["full_name"], patient["id"])
                

    def load_admissions(self):
        """Fetches and populates the dropdown with admissions."""
        try:
            # Fetch admissions with status "Admitted"
            admissions = fetch_data(self, os.getenv("ADMISSION_LIST_URL") + "?status=Admitted", self.token)
            self.populate_admission_dropdown(admissions)
        except Exception as e:
            self.show_error(str(e))

    def populate_admission_dropdown(self, admissions):
        """Populates the admission dropdown with fetched data."""
        if admissions:
            self.admission_dropdown.clear()
            self.patient_dropdown_vitals.clear()
            for admission in admissions:
                # Display patient name and admission ID
                self.admission_dropdown.addItem(
                    f"{admission['patient_name']} (Admission ID: {admission['id']})",admission['id'])
                self.patient_dropdown_vitals.addItem(f"{admission['patient_name']} (Admission ID: {admission['id']})",admission['id'])

    def load_admitted_icu(self):
        """Fetches and displays ICU admissions."""
        try:
            admissions = fetch_data(self, os.getenv("ADMISSION_LIST_URL") + "?category=ICU", self.token)
            self.populate_icu_admitted_dropdown(admissions)
        except Exception as e:
            self.show_error(str(e))

    def populate_icu_admitted_dropdown(self, icu_patients):
        """Populates the ICU admitted dropdown with fetched data."""
        if icu_patients:
            self.patient_dropdown_icu.clear()
            for admission in icu_patients:
                self.patient_dropdown_icu.addItem(f"{admission['patient_name']} (Admission {admission['id']})", admission["id"])

    def load_icu_patients(self):
        """Fetches and displays ICU patients."""
        try:
            icu_patients = fetch_data(self, os.getenv("GET_ICU_PATIENTS_URL"), self.token)
            self.populate_icu_table(icu_patients)
        except Exception as e:
            self.show_error(str(e))
    
    def load_admitted_patient(self):
        """Fetches and displays admitted patients."""
        try:
            # Fetch admitted patients data from the API
            admitted_patients = fetch_data(self, os.getenv("ADMITTED_PATIENT_URL"), self.token)
            if admitted_patients:
                self.populate_admitted_table(admitted_patients)
            else:
                self.show_error("No admitted patients found")
        except Exception as e:
            # Handle any exceptions and display an error message
            self.show_error(f"An error occurred while fetching admitted patients: {str(e)}")

    def populate_icu_table(self, icu_patients):
        """Populates the ICU table with fetched data."""
        self.icu_table.setRowCount(0)
        self.icu_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.icu_table.columnCount()):
            item = QTableWidgetItem(self.icu_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.icu_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, patient in enumerate(icu_patients, start=1):
            self.icu_table.insertRow(row)
            self.icu_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
            self.icu_table.setItem(row, 1, QTableWidgetItem(patient["status"]))
            self.icu_table.setItem(row, 2, QTableWidgetItem(patient["condition_evolution"]))
            self.icu_table.setItem(row, 3, QTableWidgetItem(patient["medications"]))
            self.icu_table.setItem(row, 4, QTableWidgetItem(patient["drips"]))
            self.icu_table.setItem(row, 5, QTableWidgetItem(patient["treatment_plan"]))
            self.icu_table.setItem(row, 6, QTableWidgetItem(patient["updated_by"]))
            self.icu_table.setItem(row, 7, QTableWidgetItem(patient["updated_at"]))
        self.icu_table.resizeColumnsToContents()

    def populate_admitted_table(self, admitted_patients):
        """Populates the admitted patients table with fetched data, including names for IDs."""
        self.admitted_table.setRowCount(0)
        self.admitted_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.admitted_table.columnCount()):
            item = QTableWidgetItem(self.admitted_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.admitted_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, patient in enumerate(admitted_patients, start=1):
                self.admitted_table.insertRow(row)
                # Add data to each column
                self.admitted_table.setItem(row, 0, QTableWidgetItem(patient.get("patient_name", "")))
                self.admitted_table.setItem(row, 1, QTableWidgetItem(patient.get("admitted_by_name", "")))
                self.admitted_table.setItem(row, 2, QTableWidgetItem(patient.get("assigned_doctor_name", "")))
                self.admitted_table.setItem(row, 3, QTableWidgetItem(patient.get("category", "")))
                self.admitted_table.setItem(row, 4, QTableWidgetItem(patient.get("department_name", "")))
                self.admitted_table.setItem(row, 5, QTableWidgetItem(patient.get("ward_name", "")))
                self.admitted_table.setItem(row, 6, QTableWidgetItem(patient.get("bed_number", "")))
                self.admitted_table.setItem(row, 7, QTableWidgetItem(patient.get("status", "")))
                self.admitted_table.setItem(row, 8, QTableWidgetItem(patient.get("admission_date", "")))
        
        self.admitted_table.resizeColumnsToContents()
    
    def load_admitted_inpatient(self):
        """Fetches and displays Inpatient admissions."""
        try:
            in_patients = fetch_data(self, os.getenv("ADMISSION_LIST_URL") + "?category=Inpatient", self.token)
            self.populate_inpatient_admitted_dropdown(in_patients)
        except Exception as e:
            self.show_error(str(e))

    def populate_inpatient_admitted_dropdown(self, in_patients):
        """Populates the Inpatient admitted dropdown with fetched data."""
        if in_patients:
            self.patient_dropdown_inpatient.clear()
            for patient in in_patients:
                self.patient_dropdown_inpatient.addItem(f"{patient['patient_name']} (Admission {patient['id']})", patient["id"])

    def load_inpatients(self):
        """Fetches and displays inpatients."""
        try:
            inpatients = fetch_data(self, os.getenv("GET_INPATIENTS_URL"), self.token)
            self.populate_inpatient_table(inpatients)
        except Exception as e:
            self.show_error(str(e))

    def populate_inpatient_table(self, inpatients):
        """Populates the Inpatient table with fetched data."""
        self.inpatient_table.setRowCount(0)
        self.inpatient_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.inpatient_table.columnCount()):
            item = QTableWidgetItem(self.inpatient_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.inpatient_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, patient in enumerate(inpatients, start=1):
            self.inpatient_table.insertRow(row)
            self.inpatient_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
            self.inpatient_table.setItem(row, 1, QTableWidgetItem(patient["status"]))
            self.inpatient_table.setItem(row, 2, QTableWidgetItem(patient["condition_evolution"]))
            self.inpatient_table.setItem(row, 3, QTableWidgetItem(patient["medications"]))
            self.inpatient_table.setItem(row, 4, QTableWidgetItem(patient["treatment_plan"]))
            self.inpatient_table.setItem(row, 5, QTableWidgetItem(patient["updated_by"]))
            self.inpatient_table.setItem(row, 6, QTableWidgetItem(patient["updated_at"]))
        self.inpatient_table.resizeColumnsToContents()
        
    def load_vitals(self):
        """Fetches and displays vitals."""
        try:
            vitals = fetch_data(self, os.getenv("GET_VITALS_URL"), self.token)
            self.populate_vital_table(vitals)
        except Exception as e:
            self.show_error(str(e))
    
    def populate_vital_table(self, vitals):
        """Populates the vital table with fetched data."""
        self.vital_table.setRowCount(0)
        self.vital_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.vital_table.columnCount()):
            item = QTableWidgetItem(self.vital_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.vital_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, patient in enumerate(vitals, start=1):
            self.vital_table.insertRow(row)
            self.vital_table.setItem(row, 0, QTableWidgetItem(patient.get("patient_name","")))
            self.vital_table.setItem(row, 1, QTableWidgetItem(str(patient.get("blood_pressure",""))))
            self.vital_table.setItem(row, 2, QTableWidgetItem(str(patient.get("heart_rate",""))))
            self.vital_table.setItem(row, 3, QTableWidgetItem(str(patient.get("temperature",""))))
            self.vital_table.setItem(row, 4, QTableWidgetItem(patient.get("recorded_by_name")))
            self.vital_table.setItem(row, 5, QTableWidgetItem(patient.get("recorded_at")))
        self.vital_table.resizeColumnsToContents()
    
    def load_departments(self):
        """Fetches and populates the dropdown with departments."""
        try:
            departments = fetch_data(self, os.getenv("DEPARTMENT_LIST_URL"), self.token)
            self.populate_department_dropdowns(departments)
        except Exception as e:
            self.show_error(str(e))

    def populate_department_dropdowns(self, departments):
        """Populates department dropdowns with fetched data."""
        if departments:
            self.department_dropdown.clear()
            for department in departments:
                self.department_dropdown.addItem(department["name"], department["id"])

    def load_wards(self):
        """Fetches and populates the dropdown with wards."""
        try:
            wards = fetch_data(self, os.getenv("WARD_LIST_URL"), self.token)
            self.populate_ward_dropdowns(wards)
        except Exception as e:
            self.show_error(str(e))

    def populate_ward_dropdowns(self, wards):
        """Populates ward dropdowns with fetched data."""
        if wards:
            self.ward_dropdown.clear()
            for ward in wards:
                self.ward_dropdown.addItem(ward["name"], ward["id"])

    def load_wards_for_department(self):
        """Fetches and populates the dropdown with wards for a selected department."""
        department_id = self.department_dropdown.currentData()
        if department_id:
            try:
                api_url = os.getenv("CREATE_WARD_URL") + f"?department_id={department_id}"
                wards = fetch_data(self, api_url, self.token)
                self.populate_ward_dropdown(wards)
            except Exception as e:
                self.show_error(str(e))

    def populate_ward_dropdown(self, wards):
        """Populates the ward dropdown with fetched data."""
        if wards:
            self.ward_dropdown.clear()
            for ward in wards:
                self.ward_dropdown.addItem(ward["name"], ward["id"])

    def load_departments_for_ward(self):
        """Fetches and populates the dropdown with departments for ward creation."""
        try:
            departments = fetch_data(self, os.getenv("DEPARTMENT_LIST_URL"), self.token)
            self.populate_department_dropdown_ward(departments)
        except Exception as e:
            self.show_error(str(e))

    def populate_department_dropdown_ward(self, departments):
        """Populates the department dropdown for ward creation."""
        if departments:
            self.department_dropdown_ward.clear()
            for department in departments:
                self.department_dropdown_ward.addItem(department["name"], department["id"])

    def load_wards_for_bed(self):
        """Fetches and populates the dropdown with wards for bed creation."""
        try:
            wards = fetch_data(self, os.getenv("WARD_LIST_URL"), self.token)
            self.populate_ward_dropdown_bed(wards)
        except Exception as e:
            self.show_error(str(e))

    def populate_ward_dropdown_bed(self, wards):
        """Populates the ward dropdown for bed creation."""
        if wards:
            self.ward_dropdown_bed.clear()
            for ward in wards:
                self.ward_dropdown_bed.addItem(ward["name"], ward["id"])

    def load_beds(self):
        """Fetches and populates the dropdown with beds."""
        try:
            beds = fetch_data(self, os.getenv("BED_LIST_URL"), self.token)
            self.populate_bed_dropdowns(beds)
        except Exception as e:
            self.show_error(str(e))

    def populate_bed_dropdowns(self, beds):
        """Populates bed dropdowns with fetched data."""
        if beds:
            self.bed_dropdown.clear()
            for bed in beds:
                self.bed_dropdown.addItem(str(bed["bed_number"]), bed["id"])

    def load_beds_for_ward(self):
        """Fetches and populates the dropdown with beds for a selected ward."""
        ward_id = self.ward_dropdown.currentData()
        if ward_id:
            try:
                api_url = os.getenv("BED_LIST_URL") + f"?ward_id={ward_id}&is_occupied=False"
                beds = fetch_data(self, api_url, self.token)
                self.populate_bed_dropdown(beds)
            except Exception as e:
                self.show_error(str(e))

    def populate_bed_dropdown(self, beds):
        """Populates the bed dropdown with fetched data."""
        if beds:
            self.bed_dropdown.clear()
            for bed in beds:
                self.bed_dropdown.addItem(str(bed["bed_number"]), bed["id"])

    def load_existing_departments(self):
        """Fetches and displays existing departments."""
        try:
            departments = fetch_data(self, os.getenv("DEPARTMENT_LIST_URL"), self.token)
            self.populate_existing_departments(departments)
        except Exception as e:
            self.show_error(str(e))

    def populate_existing_departments(self, departments):
        """Populates the existing department table with fetched data."""
        self.existing_department_table.setRowCount(0)
        self.existing_department_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.existing_department_table.columnCount()):
            item = QTableWidgetItem(self.existing_department_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.existing_department_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, department in enumerate(departments, start=1):
            self.existing_department_table.insertRow(row)
            self.existing_department_table.setItem(row, 0, QTableWidgetItem(str(department["id"])))
            self.existing_department_table.setItem(row, 1, QTableWidgetItem(department["name"]))
            self.existing_department_table.setItem(row, 2, QTableWidgetItem(department["category"]))
        self.existing_department_table.resizeColumnsToContents()

    def load_existing_wards(self):
        """Fetches and displays existing wards."""
        try:
            wards = fetch_data(self, os.getenv("WARD_LIST_URL"), self.token)
            self.populate_existing_wards(wards)
        except Exception as e:
            self.show_error(str(e))

    def populate_existing_wards(self, wards):
        """Populates the existing ward table with fetched data."""
        self.existing_ward_table.setRowCount(0)
        self.existing_ward_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.existing_ward_table.columnCount()):
            item = QTableWidgetItem(self.existing_ward_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.existing_ward_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, ward in enumerate(wards, start=1):
            self.existing_ward_table.insertRow(row)
            self.existing_ward_table.setItem(row, 0, QTableWidgetItem(str(ward["id"])))
            self.existing_ward_table.setItem(row, 1, QTableWidgetItem(ward["name"]))
            self.existing_ward_table.setItem(row, 2, QTableWidgetItem(str(ward["department_id"])))
        self.existing_ward_table.resizeColumnsToContents()

    def load_existing_beds(self):
        """Fetches and displays existing beds."""
        try:
            beds = fetch_data(self, os.getenv("BED_LIST_URL"), self.token)
            self.populate_existing_beds(beds)
        except Exception as e:
            self.show_error(str(e))

    def populate_existing_beds(self, beds):
        """Populates the existing bed table with fetched data."""
        self.existing_bed_table.setRowCount(0)
        self.existing_bed_table.insertRow(0)
        
        # Add duplicate header at the top
        for col in range(self.existing_bed_table.columnCount()):
            item = QTableWidgetItem(self.existing_bed_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.existing_bed_table.setItem(0, col, item)
        
        # Populate the table with data
        for row, bed in enumerate(beds, start=1):
            self.existing_bed_table.insertRow(row)
            self.existing_bed_table.setItem(row, 0, QTableWidgetItem(str(bed["id"])))
            self.existing_bed_table.setItem(row, 1, QTableWidgetItem(str(bed["bed_number"])))
            self.existing_bed_table.setItem(row, 2, QTableWidgetItem(str(bed["ward_id"])))
        self.existing_bed_table.resizeColumnsToContents()

    def show_error(self, error_message):
        """Displays an error message in the main thread."""
        QMessageBox.critical(self, "Error", error_message)

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
            self.load_admitted_patient()
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
        status = self.status_input_inpatient.currentText().strip()
        condition_evolution = self.condition_evolution_input_inpatient.toPlainText().strip()
        medications = self.medications_input_inpatient.toPlainText().strip()
        treatment_plan = self.treatment_plan_input_inpatient.toPlainText().strip()

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
            self.load_existing_wards()
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
        self.load_vitals()
        self.load_admitted_patient()
        self.load_inpatients()
        self.load_existing_departments()
        self.load_existing_wards()
        self.load_existing_beds()
        self.status_bar.showMessage("All data refreshed successfully.", 3000)