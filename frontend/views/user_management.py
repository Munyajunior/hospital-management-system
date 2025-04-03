from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QMessageBox, QHBoxLayout, QComboBox, QToolButton,
    QLineEdit, QHeaderView, QApplication, QGroupBox, QFormLayout, QTabWidget, 
    QScrollArea, QToolBar, QStatusBar, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction, QFont
from utils.api_utils import fetch_data, post_data, delete_data, update_data
import os
from typing import Optional, Dict, List

class UserManagement(QWidget):
    theme_changed = Signal(bool)  # Signal to notify theme changes
    
    def __init__(self, role: str, user_id: int, auth_token: str):
        super().__init__()
        self.token = auth_token
        self.role = role
        self.user_id = user_id
        self.is_dark_theme = False  # Initialize theme state
        self.current_staff_data = {}  # Store current staff data
        self.current_patient_data = {}  # Store current patient data

        self.authenticate_user()
        self.init_ui()
        self.load_staff()
        self.load_patients()

    def authenticate_user(self) -> None:
        """Check if user is authenticated and has proper permissions."""
        if not self.token:
            QMessageBox.critical(self, "Access Denied", "You must be logged in to access this page.")
            self.close()
            return
        
        if self.role not in ["admin"]:
            QMessageBox.critical(self, "Access Denied", "You do not have permission to access this module.")
            self.close()
            return

    def init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("User Management")
        self.setWindowIcon(QIcon("assets/icons/users.png"))
        self.setup_window_geometry()
        
        layout = QVBoxLayout()
        self.setup_toolbar_and_statusbar(layout)
        self.setup_tabs(layout)
        
        self.setLayout(layout)
        self.apply_theme()

    def setup_window_geometry(self) -> None:
        """Set up window size and position."""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.resize(int(screen_geometry.width() * 0.8), int(screen_geometry.height() * 0.8))
        self.setMinimumSize(800, 600)
        self.move(screen_geometry.center() - self.rect().center())

    def setup_toolbar_and_statusbar(self, layout: QVBoxLayout) -> None:
        """Set up toolbar and status bar."""
        # Toolbar
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)

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
        layout.addWidget(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_tabs(self, layout: QVBoxLayout) -> None:
        """Set up the tab widget with staff and patient tabs."""
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Staff management Tab
        self.staff_tab = QWidget()
        self.init_staff_tab()
        self.tabs.addTab(self.staff_tab, QIcon("assets/icons/staff.png"), "Manage Staff")
        
        # Patient management Tab
        self.patients_tab = QWidget()
        self.init_patients_tab()
        self.tabs.addTab(self.patients_tab, QIcon("assets/icons/patients.png"), "Manage Patients")

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        self.theme_changed.emit(self.is_dark_theme)  # Emit signal for theme change

    def apply_theme(self) -> None:
        """Apply the current theme (light or dark)."""
        theme_file = "dark_theme.qss" if self.is_dark_theme else "light_theme.qss"
        try:
            with open(f"assets/themes/{theme_file}", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            self.apply_default_theme()
        
        self.toggle_theme_action.setText("🌙 Dark Theme" if self.is_dark_theme else "☀️ Light Theme")

    def apply_default_theme(self) -> None:
        """Apply default theme if theme files are not found."""
        base_style = """
            QWidget {
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            QTableWidget {
                alternate-background-color: #F8F9F9;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        
        if self.is_dark_theme:
            self.setStyleSheet(base_style + """
                QWidget {
                    background-color: #2C3E50;
                    color: #ECF0F1;
                }
                QLabel {
                    color: #ECF0F1;
                }
                QTableWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    alternate-background-color: #2C3E50;
                }
                QLineEdit, QComboBox, QTextEdit, QListWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    border: 1px solid #5D6D7E;
                }
            """)
        else:
            self.setStyleSheet(base_style + """
                QWidget {
                    background-color: #F4F6F7;
                    color: #2C3E50;
                }
                QLabel {
                    color: #2C3E50;
                }
                QTableWidget {
                    background-color: white;
                    color: #2C3E50;
                }
                QLineEdit, QComboBox, QTextEdit, QListWidget {
                    background-color: white;
                    color: #2C3E50;
                    border: 1px solid #D5DBDB;
                }
            """)

    def init_staff_tab(self) -> None:
        """Initialize the staff management tab."""
        layout = QVBoxLayout()
        
        # Staff Table
        table_group = QGroupBox("Registered Staff")
        table_layout = QVBoxLayout()

        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(6)
        self.staff_table.setHorizontalHeaderLabels(["User ID", "Name", "Role", "Is Active", "Activate/Deactivate", "Delete"])
        self.staff_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.staff_table.verticalHeader().setVisible(False)
        self.staff_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.staff_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set fixed row height and show 10 rows by default
        self.staff_table.verticalHeader().setDefaultSectionSize(30)  # 30 pixels per row
        self.staff_table.setRowCount(10)  # Show 10 empty rows initially
        
        table_layout.addWidget(self.staff_table)
        self.add_duplicate_header(self.staff_table)

        if self.role == "admin":  
            self.add_staff_section(layout)
            self.update_staff_section(layout)

        self.refresh_button = QPushButton("Refresh Staff")
        self.refresh_button.clicked.connect(self.load_staff)
        table_layout.addWidget(self.refresh_button)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        self.staff_tab.setLayout(layout)

    def init_patients_tab(self) -> None:
        """Initialize the patient management tab."""
        layout = QVBoxLayout()
        
        # Patient Table
        table_group = QGroupBox("Registered Patients")
        table_layout = QVBoxLayout()

        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(6)
        self.patient_table.setHorizontalHeaderLabels(["Patient ID", "Name", "Email", "Is Active", "Activate/Deactivate", "Delete"])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patient_table.verticalHeader().setVisible(False)
        self.patient_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.patient_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Set fixed row height and show 10 rows by default
        self.patient_table.verticalHeader().setDefaultSectionSize(30)  # 30 pixels per row
        self.patient_table.setRowCount(10)  # Show 10 empty rows initially
        
        table_layout.addWidget(self.patient_table)
        self.add_duplicate_header(self.patient_table)

        if self.role == "admin":  
            self.add_patient_section(layout)
            self.update_patient_section(layout)

        self.refresh_button = QPushButton("Refresh Patients")
        self.refresh_button.clicked.connect(self.load_patients)
        table_layout.addWidget(self.refresh_button)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
        self.patients_tab.setLayout(layout)
        
    def add_duplicate_header(self, table: QTableWidget) -> None:
        """Adds a duplicate header at the bottom of the table."""
        table.setRowCount(table.rowCount() + 1)
        for col in range(table.columnCount()):
            item = QTableWidgetItem(table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            item.setFlags(Qt.ItemIsEnabled)  # Make non-editable
            table.setItem(table.rowCount() - 1, col, item)
            
    def add_staff_section(self, layout: QVBoxLayout) -> None:
        """Admin-only section for adding new staff."""
        add_group = QGroupBox("Add New Staff")
        form_layout = QFormLayout()

        # Name Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name")
        form_layout.addRow("Full Name:", self.name_input)

        # Email Input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter valid email")
        form_layout.addRow("Email:", self.email_input)
        
        # Password Input with toggle
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)

        self.toggle_add_staff_password_button = QToolButton()
        self.toggle_add_staff_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))
        self.toggle_add_staff_password_button.setCheckable(True)
        self.toggle_add_staff_password_button.toggled.connect(self.toggle_add_staff_password_visibility)
        password_layout.addWidget(self.toggle_add_staff_password_button)
        form_layout.addRow("Password:", password_layout)

        # Role Selection
        self.role_select = QComboBox()
        self.role_select.addItems(["Select role...","doctor", "nurse", "pharmacist", "lab_technician", "radiologist", "admin", "icu"])
        self.role_select.setCurrentIndex(0) 
        form_layout.addRow("Role:", self.role_select)

        # Add Button
        self.add_staff_button = QPushButton("Add Staff")
        self.add_staff_button.clicked.connect(self.add_staff)
        form_layout.addRow(self.add_staff_button)

        add_group.setLayout(form_layout)
        layout.addWidget(add_group)
        
    def add_patient_section(self, layout: QVBoxLayout) -> None:
        """Admin-only section for adding new patients."""
        add_group = QGroupBox("Add New Patient")
        form_layout = QFormLayout()

        # Name Input
        self.patient_name_input = QLineEdit()
        self.patient_name_input.setPlaceholderText("Enter full name")
        form_layout.addRow("Full Name:", self.patient_name_input)

        # Email Input
        self.patient_email_input = QLineEdit()
        self.patient_email_input.setPlaceholderText("Enter valid email")
        form_layout.addRow("Email:", self.patient_email_input)
        
        # Password Input with toggle
        password_layout = QHBoxLayout()
        self.patient_password_input = QLineEdit()
        self.patient_password_input.setPlaceholderText("Enter password")
        self.patient_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.patient_password_input)

        self.toggle_add_patient_password_button = QToolButton()
        self.toggle_add_patient_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))
        self.toggle_add_patient_password_button.setCheckable(True)
        self.toggle_add_patient_password_button.toggled.connect(self.toggle_add_patient_password_visibility)
        password_layout.addWidget(self.toggle_add_patient_password_button)
        form_layout.addRow("Password:", password_layout)

        # Add Button
        self.add_patient_button = QPushButton("Add Patient")
        self.add_patient_button.clicked.connect(self.add_patient)
        form_layout.addRow(self.add_patient_button)

        add_group.setLayout(form_layout)
        layout.addWidget(add_group)
    
    def update_staff_section(self, layout: QVBoxLayout) -> None:
        """Section for updating staff information."""
        update_group = QGroupBox("Update Staff Information")
        update_layout = QFormLayout()

        # Staff Selection
        self.staff_select = QComboBox()
        self.staff_select.addItem("Select staff...", None)
        update_layout.addRow("Staff:", self.staff_select)

        # New Email Input
        self.new_email_input = QLineEdit()
        self.new_email_input.setPlaceholderText("Enter new email")
        update_layout.addRow("New Email:", self.new_email_input)

        # Password Input with toggle
        password_layout = QHBoxLayout()
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.new_password_input)

        self.toggle_password_button = QToolButton()
        self.toggle_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.toggled.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_button)
        update_layout.addRow("New Password:", password_layout)
        
        # Update Button
        self.update_staff_button = QPushButton("Update Staff")
        self.update_staff_button.clicked.connect(self.update_staff_info)
        update_layout.addRow(self.update_staff_button)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)

        # Connect staff selection change
        self.staff_select.currentIndexChanged.connect(self.on_staff_selected)

    def update_patient_section(self, layout: QVBoxLayout) -> None:
        """Section for updating patient information."""
        update_group = QGroupBox("Update Patient Information")
        update_layout = QFormLayout()

        # Patient Selection
        self.patient_select = QComboBox()
        self.patient_select.addItem("Select patient...", None)
        update_layout.addRow("Patient:", self.patient_select)

        # New Email Input
        self.new_patient_email_input = QLineEdit()
        self.new_patient_email_input.setPlaceholderText("Enter new email")
        update_layout.addRow("New Email:", self.new_patient_email_input)

        # Password Input with toggle
        password_layout = QHBoxLayout()
        self.new_patient_password_input = QLineEdit()
        self.new_patient_password_input.setPlaceholderText("Enter new password")
        self.new_patient_password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.new_patient_password_input)

        self.toggle_patient_password_button = QToolButton()
        self.toggle_patient_password_button.setIcon(QIcon("assets/icons/eye-crossed.png"))
        self.toggle_patient_password_button.setCheckable(True)
        self.toggle_patient_password_button.toggled.connect(self.toggle_patient_password_visibility)
        password_layout.addWidget(self.toggle_patient_password_button)
        update_layout.addRow("New Password:", password_layout)
        
        # Update Button
        self.update_patient_button = QPushButton("Update Patient")
        self.update_patient_button.clicked.connect(self.update_patient_info)
        update_layout.addRow(self.update_patient_button)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)

        # Connect patient selection change
        self.patient_select.currentIndexChanged.connect(self.on_patient_selected)

    def on_staff_selected(self, index: int) -> None:
        """Handle staff selection change."""
        if index > 0:  # Skip the "Select staff..." item
            staff_id = self.staff_select.currentData()
            staff = self.current_staff_data.get(staff_id)
            if staff:
                self.new_email_input.setText(staff.get("email", ""))
                self.new_password_input.clear()

    def on_patient_selected(self, index: int) -> None:
        """Handle patient selection change."""
        if index > 0:  # Skip the "Select patient..." item
            patient_id = self.patient_select.currentData()
            patient = self.current_patient_data.get(patient_id)
            if patient:
                self.new_patient_email_input.setText(patient.get("email", ""))
                self.new_patient_password_input.clear()

    def load_staff(self) -> None:
        """Fetch staff data from the backend API."""
        api_url = os.getenv("USER_URL")
        staff = fetch_data(self, api_url, self.token)
        
        if staff is not None:
            self.current_staff_data = {s["id"]: s for s in staff}
            self.populate_staff_table(staff)
            self.populate_staff_combobox(staff)
        else:
            QMessageBox.critical(self, "Error", "Failed to load staff data.")

    def populate_staff_table(self, staff: List[Dict]) -> None:
        """Populate the staff table with data."""
        self.staff_table.setRowCount(0)
        self.add_duplicate_header(self.staff_table)

        for row, staff_member in enumerate(staff, start=1):
            self.staff_table.insertRow(row)
            
            # Add data columns
            self.staff_table.setItem(row, 0, QTableWidgetItem(str(staff_member["id"])))
            self.staff_table.setItem(row, 1, QTableWidgetItem(staff_member["full_name"]))
            self.staff_table.setItem(row, 2, QTableWidgetItem(staff_member["role"]))
            
            # Active status with colored text
            active_item = QTableWidgetItem("Yes" if staff_member["is_active"] else "No")
            active_item.setForeground(Qt.darkGreen if staff_member["is_active"] else Qt.darkRed)
            self.staff_table.setItem(row, 3, active_item)

            # Action buttons
            if self.role == "admin":
                self.add_action_buttons(row, staff_member)

    def populate_staff_combobox(self, staff: List[Dict]) -> None:
        """Populate the staff selection combobox."""
        self.staff_select.clear()
        self.staff_select.addItem("Select staff...", None)
        
        for staff_member in staff:
            self.staff_select.addItem(
                f"{staff_member['full_name']} ({staff_member['role']})", 
                staff_member["id"]
            )

    def add_action_buttons(self, row: int, staff_member: Dict) -> None:
        """Add action buttons to the staff table."""
        # Activate/Deactivate Button
        btn_text = "Deactivate" if staff_member["is_active"] else "Activate"
        btn_color = "#ffc107" if staff_member["is_active"] else "#28a745"
        
        activate_button = QPushButton(btn_text)
        activate_button.setStyleSheet(f"background-color: {btn_color}; color: white;")
        activate_button.clicked.connect(
            lambda _, u_id=staff_member["id"]: self.toggle_staff_status(u_id))
        self.staff_table.setCellWidget(row, 4, activate_button)

        # Delete Button
        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: #dc3545; color: white;")
        delete_button.clicked.connect(
            lambda _, u_id=staff_member["id"]: self.delete_staff(u_id))
        self.staff_table.setCellWidget(row, 5, delete_button)

    def load_patients(self) -> None:
        """Fetch patient data from the backend API."""
        api_url = os.getenv("PATIENT_LIST_URL")
        patients = fetch_data(self, api_url, self.token)
        
        if patients is not None:
            self.current_patient_data = {p["id"]: p for p in patients}
            self.populate_patient_table(patients)
            self.populate_patient_combobox(patients)
        else:
            QMessageBox.critical(self, "Error", "Failed to load patient data.")

    def populate_patient_table(self, patients: List[Dict]) -> None:
        """Populate the patient table with data."""
        self.patient_table.setRowCount(0)
        self.add_duplicate_header(self.patient_table)

        for row, patient in enumerate(patients, start=1):
            self.patient_table.insertRow(row)
            
            # Add data columns
            self.patient_table.setItem(row, 0, QTableWidgetItem(str(patient["id"])))
            self.patient_table.setItem(row, 1, QTableWidgetItem(patient["full_name"]))
            self.patient_table.setItem(row, 2, QTableWidgetItem(patient.get("email", "")))
            
            # Active status with colored text
            active_item = QTableWidgetItem("Yes" if patient["is_active"] else "No")
            active_item.setForeground(Qt.darkGreen if patient["is_active"] else Qt.darkRed)
            self.patient_table.setItem(row, 3, active_item)

            # Action buttons
            if self.role == "admin":
                self.add_patient_action_buttons(row, patient)

    def populate_patient_combobox(self, patients: List[Dict]) -> None:
        """Populate the patient selection combobox."""
        self.patient_select.clear()
        self.patient_select.addItem("Select patient...", None)
        
        for patient in patients:
            self.patient_select.addItem(
                f"{patient['full_name']} ({patient.get('email', '')})", 
                patient["id"]
            )

    def add_patient_action_buttons(self, row: int, patient: Dict) -> None:
        """Add action buttons to the patient table."""
        # Activate/Deactivate Button
        btn_text = "Deactivate" if patient["is_active"] else "Activate"
        btn_color = "#ffc107" if patient["is_active"] else "#28a745"
        
        activate_button = QPushButton(btn_text)
        activate_button.setStyleSheet(f"background-color: {btn_color}; color: white;")
        activate_button.clicked.connect(
            lambda _, p_id=patient["id"]: self.toggle_patient_status(p_id))
        self.patient_table.setCellWidget(row, 4, activate_button)

        # Delete Button
        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: #dc3545; color: white;")
        delete_button.clicked.connect(
            lambda _, p_id=patient["id"]: self.delete_patient(p_id))
        self.patient_table.setCellWidget(row, 5, delete_button)

    def add_staff(self) -> None:
        """Handle adding a new staff member."""
        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_select.currentText().strip()

        if not self.validate_staff_inputs(full_name, email, password, role):
            return
            
        api_url = os.getenv("ADD_USER_URL")
        data = {
            "full_name": full_name, 
            "email": email,
            "password": password,
            "role": role
        }
        
        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Staff added successfully.")
            self.clear_staff_inputs()
            self.load_staff()
        else:
            QMessageBox.critical(self, "Error", "Failed to add staff.")

    def validate_staff_inputs(self, full_name: str, email: str, password: str, role: str) -> bool:
        """Validate staff input fields."""
        if not all([full_name, email, password, role]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return False
            
        if "@" not in email:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return False
            
        if len(password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return False
        
        if role == "Select role...":
            QMessageBox.warning(self, "Input Error", "Please select a role.")
            return False
            
        return True

    def clear_staff_inputs(self) -> None:
        """Clear staff input fields."""
        self.name_input.clear()
        self.email_input.clear()
        self.password_input.clear()
        self.role_select.setCurrentIndex(0)

    def add_patient(self) -> None:
        """Handle adding a new patient."""
        full_name = self.patient_name_input.text().strip()
        email = self.patient_email_input.text().strip()
        password = self.patient_password_input.text().strip()

        if not self.validate_patient_inputs(full_name, email, password):
            return
            
        api_url = os.getenv("REGISTER_PATIENT_URL")
        data = {
            "full_name": full_name, 
            "email": email,
            "password": password
        }
        
        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Patient added successfully.")
            self.clear_patient_inputs()
            self.load_patients()
        else:
            QMessageBox.critical(self, "Error", "Failed to add patient.")

    def validate_patient_inputs(self, full_name: str, email: str, password: str) -> bool:
        """Validate patient input fields."""
        if not all([full_name, email, password]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return False
            
        if "@" not in email:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return False
            
        if len(password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return False
            
        return True

    def clear_patient_inputs(self) -> None:
        """Clear patient input fields."""
        self.patient_name_input.clear()
        self.patient_email_input.clear()
        self.patient_password_input.clear()

    def delete_staff(self, staff_id: int) -> None:
        """Handle staff deletion with confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this staff member?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            base_url = os.getenv("USER_URL")
            api_url = f"{base_url}{staff_id}"
            response = delete_data(self, api_url, self.token)
            
            if response:
                QMessageBox.information(self, "Success", "Staff deleted successfully.")
                self.load_staff()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete staff.")

    def delete_patient(self, patient_id: int) -> None:
        """Handle patient deletion with confirmation."""
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this patient?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            base_url = os.getenv("PATIENT_LIST_URL")
            api_url = f"{base_url}{patient_id}"
            response = delete_data(self, api_url, self.token)
            
            if response:
                QMessageBox.information(self, "Success", "Patient deleted successfully.")
                self.load_patients()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete patient.")

    def toggle_staff_status(self, staff_id: int) -> None:
        """Toggle staff active status."""
        staff = self.current_staff_data.get(staff_id)
        if not staff:
            return
            
        new_status = not staff["is_active"]
        base_url = os.getenv("USER_URL")
        api_url = f"{base_url}{staff_id}/is_active"
        data = {"is_active": new_status}

        response = update_data(self, api_url, data, self.token)
        if response:
            message = "Staff activated successfully." if new_status else "Staff deactivated successfully."
            QMessageBox.information(self, "Success", message)
            self.load_staff()
        else:
            QMessageBox.critical(self, "Error", "Failed to update staff status.")

    def toggle_patient_status(self, patient_id: int) -> None:
        """Toggle patient active status."""
        patient = self.current_patient_data.get(patient_id)
        if not patient:
            return
            
        new_status = not patient["is_active"]
        base_url = os.getenv("PATIENT_URL")
        api_url = f"{base_url}{patient_id}/is_active"
        data = {"is_active": new_status}

        response = update_data(self, api_url, data, self.token)
        if response:
            message = "Patient activated successfully." if new_status else "Patient deactivated successfully."
            QMessageBox.information(self, "Success", message)
            self.load_patients()
        else:
            QMessageBox.critical(self, "Error", "Failed to update patient status.")

    def update_staff_info(self) -> None:
        """Update staff information."""
        staff_id = self.staff_select.currentData()
        if not staff_id:
            QMessageBox.warning(self, "Selection Error", "Please select a staff member.")
            return

        new_email = self.new_email_input.text().strip()
        new_password = self.new_password_input.text().strip()

        if not new_email and not new_password:
            QMessageBox.warning(self, "Input Error", "Please enter at least one field to update.")
            return
            
        if new_email and "@" not in new_email:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return
            
        if new_password and len(new_password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return

        data = {}
        if new_email:
            data["email"] = new_email
        if new_password:
            data["password"] = new_password

        base_url = os.getenv("USER_URL")
        api_url = f"{base_url}{staff_id}/update"
        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Staff updated successfully.")
            self.new_email_input.clear()
            self.new_password_input.clear()
            self.load_staff()
        else:
            QMessageBox.critical(self, "Error", "Failed to update staff.")

    def update_patient_info(self) -> None:
        """Update patient information."""
        patient_id = self.patient_select.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Selection Error", "Please select a patient.")
            return

        new_email = self.new_patient_email_input.text().strip()
        new_password = self.new_patient_password_input.text().strip()

        if not new_email and not new_password:
            QMessageBox.warning(self, "Input Error", "Please enter at least one field to update.")
            return
            
        if new_email and "@" not in new_email:
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return
            
        if new_password and len(new_password) < 8:
            QMessageBox.warning(self, "Input Error", "Password must be at least 8 characters long.")
            return

        data = {}
        if new_email:
            data["email"] = new_email
        if new_password:
            data["password"] = new_password

        base_url = os.getenv("PATIENT_URL")
        api_url = f"{base_url}{patient_id}/update"
        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Patient updated successfully.")
            self.new_patient_email_input.clear()
            self.new_patient_password_input.clear()
            self.load_patients()
        else:
            QMessageBox.critical(self, "Error", "Failed to update patient.")

    def toggle_add_staff_password_visibility(self, checked: bool) -> None:
        """Toggle staff password visibility during addition."""
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.toggle_add_staff_password_button.setIcon(
            QIcon("assets/icons/eye.png" if checked else "assets/icons/eye-crossed.png")
        )

    def toggle_add_patient_password_visibility(self, checked: bool) -> None:
        """Toggle patient password visibility during addition."""
        self.patient_password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.toggle_add_patient_password_button.setIcon(
            QIcon("assets/icons/eye.png" if checked else "assets/icons/eye-crossed.png")
        )

    def toggle_password_visibility(self, checked: bool) -> None:
        """Toggle password visibility during update."""
        self.new_password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.toggle_password_button.setIcon(
            QIcon("assets/icons/eye.png" if checked else "assets/icons/eye-crossed.png")
        )

    def toggle_patient_password_visibility(self, checked: bool) -> None:
        """Toggle patient password visibility during update."""
        self.new_patient_password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        self.toggle_patient_password_button.setIcon(
            QIcon("assets/icons/eye.png" if checked else "assets/icons/eye-crossed.png")
        )

    def refresh_all(self) -> None:
        """Refresh all data."""
        self.load_staff()
        self.load_patients()
        self.status_bar.showMessage("Data refreshed successfully", 3000)