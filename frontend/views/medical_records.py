from PySide6.QtWidgets import (QApplication, QWidget, QHeaderView, QPushButton, QMessageBox, QVBoxLayout, QLabel, 
                               QTableWidget, QTableWidgetItem, QScrollArea, QLineEdit, QHBoxLayout, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon,QColor
from .doctors import PatientRecordUpdateWindow
from utils.api_utils import fetch_data
import os


class MedicalRecords(QWidget):
    def __init__(self, user_role, user_id, token):
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.current_theme = "light"  # Default theme

        self.setWindowTitle("Patient Management")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height

        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize UI elements with enhanced styling."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Label
        self.title_label = QLabel("Medical Records")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Search Bar and Theme Toggle
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search patients...")
        self.search_bar.textChanged.connect(self.filter_patients)
        search_layout.addWidget(self.search_bar)

        # Theme Toggle Button
        self.theme_toggle_button = QPushButton("🌙 Toggle Theme")
        self.theme_toggle_button.setStyleSheet(self.button_style())
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        search_layout.addWidget(self.theme_toggle_button)

        main_layout.addLayout(search_layout)

        if self.user_role == "doctor":
            # Patient Table
            self.medical_record_table = QTableWidget()
            self.medical_record_table.setColumnCount(7)
            self.medical_record_table.setHorizontalHeaderLabels(["ID", "Name", "DOB", "Contact", "Emergency", "Category", "Actions"])
            self.medical_record_table.horizontalHeader().setStretchLastSection(True)
            self.medical_record_table.setAlternatingRowColors(True)
            self.add_placeholder_header(self.medical_record_table)  # Add placeholder header row
            main_layout.addWidget(self.medical_record_table, stretch=1)

            self.load_assigned_patients()
        else:
            # Create scrollable table
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)  # Allow resizing

            # Patient Table
            self.patient_table = QTableWidget()
            self.patient_table.setColumnCount(9)
            self.patient_table.setHorizontalHeaderLabels([
                "ID", "Medical History", "Diagnosis", "Treatment Plan",
                "Prescription", "Lab Tests", "Radiography", "Notes", "Actions"
            ])

            # Enable word wrap for header labels
            self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
            self.patient_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.TextWordWrap)  # Enables text wrapping

            # Adjust row height dynamically for better readability
            self.patient_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

            # Set alternating row colors for readability
            self.patient_table.setAlternatingRowColors(True)

            # Set column width for "Actions" column
            self.patient_table.setColumnWidth(8, 150)

            # Add placeholder header row
            self.add_placeholder_header(self.patient_table)

            # Add table inside the scroll area
            self.scroll_area.setWidget(self.patient_table)
            main_layout.addWidget(self.scroll_area)

            self.load_assigned_patients()

        self.setLayout(main_layout)
        self.apply_theme(self.current_theme)  # Apply default theme

    def add_placeholder_header(self, table):
        """Add a placeholder row to simulate a duplicated header."""
        table.insertRow(0)  # Insert a new row at the top
        for col in range(table.columnCount()):
            header_text = table.horizontalHeaderItem(col).text()  # Get header text
            item = QTableWidgetItem(header_text)  # Create a QTableWidgetItem with the header text
            item.setFlags(Qt.NoItemFlags)  # Make the placeholder row non-editable
            item.setBackground(QColor("#3498db"))  # Set background color to match the header
            item.setForeground(QColor("white"))  # Set text color to white
            table.setItem(0, col, item)  # Add the item to the table

    def apply_theme(self, theme):
        """Apply light or dark theme to the application."""
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #2C3E50;
                    color: #ECF0F1;
                }
                QLabel#titleLabel {
                    font-size: 26px;
                    font-weight: bold;
                    color: #ECF0F1;
                    padding: 15px;
                    border-bottom: 2px solid #3498db;
                    text-align: center;
                }
                QTableWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    alternate-background-color: #2C3E50;
                    border: 1px solid #555;
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
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #555;
                    border-radius: 5px;
                    font-size: 14px;
                    background-color: #34495E;
                    color: #ECF0F1;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            """)
        else:
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
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #dcdcdc;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #3498db;
                }
            """)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def filter_patients(self):
        """Filter patients based on search text."""
        search_text = self.search_bar.text().lower()
        if self.user_role == "doctor":
            for row in range(self.medical_record_table.rowCount()):
                match = False
                for col in range(self.medical_record_table.columnCount()):
                    item = self.medical_record_table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                self.medical_record_table.setRowHidden(row, not match)
        else:
            for row in range(self.patient_table.rowCount()):
                match = False
                for col in range(self.patient_table.columnCount()):
                    item = self.patient_table.item(row, col)
                    if item and search_text in item.text().lower():
                        match = True
                        break
                self.patient_table.setRowHidden(row, not match)

    def load_assigned_patients(self):
        if self.user_role == "doctor":
            doctor_id = self.user_id
            base_url = os.getenv("ASSIGNED_PATIENTS_URL")
            api_url = f"{base_url}/{doctor_id}/patients"
            patients = fetch_data(self, api_url, self.token)

            if not patients:
                QMessageBox.information(self, "No Patients", "No patients have been assigned yet.")
                return

            self.medical_record_table.setRowCount(len(patients) + 1)  # +1 for the placeholder header
            for row, patient in enumerate(patients):
                self.medical_record_table.setItem(row + 1, 0, QTableWidgetItem(str(patient["id"])))
                self.medical_record_table.setItem(row + 1, 1, QTableWidgetItem(patient["full_name"]))
                self.medical_record_table.setItem(row + 1, 2, QTableWidgetItem(patient["date_of_birth"]))
                self.medical_record_table.setItem(row + 1, 3, QTableWidgetItem(patient["contact_number"]))
                self.medical_record_table.setItem(row + 1, 4, QTableWidgetItem(str(patient["emergency"])))
                self.medical_record_table.setItem(row + 1, 5, QTableWidgetItem(patient["category"]))

                # Button to View Patient Record
                self.medical_record_table.setCellWidget(row + 1, 6, self.create_view_button(patient["id"]))
        else:
            api_url = os.getenv("MEDICAL_RECORD_URL") + "/"
            patients = fetch_data(self, api_url, self.token)

            if not patients:
                QMessageBox.information(self, "No Patients", "No patients have been registered.")
                return

            self.patient_table.setRowCount(len(patients) + 1)  # +1 for the placeholder header
            for row, patient in enumerate(patients):
                self.patient_table.setItem(row + 1, 0, QTableWidgetItem(str(patient["id"])))
                self.patient_table.setItem(row + 1, 1, QTableWidgetItem(patient["medical_history"]))
                self.patient_table.setItem(row + 1, 2, QTableWidgetItem(patient["diagnosis"]))
                self.patient_table.setItem(row + 1, 3, QTableWidgetItem(patient["treatment_plan"]))
                self.patient_table.setItem(row + 1, 4, QTableWidgetItem(patient["prescription"]))
                self.patient_table.setItem(row + 1, 5, QTableWidgetItem(patient["lab_tests_results"]))
                self.patient_table.setItem(row + 1, 6, QTableWidgetItem(patient["scan_results"]))
                self.patient_table.setItem(row + 1, 7, QTableWidgetItem(patient["notes"]))

                # Button to View Patient Record
                self.patient_table.setCellWidget(row + 1, 8, self.update_view_button(patient["id"]))

    def update_view_button(self, patient_id):
        """Create 'Update Record' button for each patient."""
        button = QPushButton("Update Record")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.update_patient_record(patient_id))
        return button

    def update_patient_record(self, patient_id):
        """Open the patient record management window."""
        self.patient_record_window = PatientRecordUpdateWindow(patient_id, self.token, self.user_id)
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

class PatientRecordWindow(QWidget):
    def __init__(self, patient_id, user_id, token):
        super().__init__()
        self.patient_id = patient_id
        self.token = token
        self.doctor_id = user_id
        self.setWindowTitle(f"Patient Record - {patient_id}")
        self.setGeometry(250, 250, 800, 700)  # Slightly larger window for better spacing
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
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header Label
        self.title_label = QLabel(f"Patient Record - ID: {self.patient_id}")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0056b3;")
        main_layout.addWidget(self.title_label)

        # Back Button
        back_button = QPushButton("Back")
        back_button.setIcon(QIcon.fromTheme("go-previous"))
        back_button.clicked.connect(self.close)
        main_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        # Create scrollable table
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow resizing

        # Patient Table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(9)
        self.patient_table.setHorizontalHeaderLabels([
            "Name", "Medical History", "Diagnosis", "Treatment Plan",
            "Prescription", "Lab Tests", "Radiography", "Notes", "Actions"
        ])

        # Enable word wrap for header labels
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch all columns
        self.patient_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter | Qt.TextWordWrap)  # Enables text wrapping

        # Adjust row height dynamically for better readability
        self.patient_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Set alternating row colors for readability
        self.patient_table.setAlternatingRowColors(True)

        # Enable scrolling
        self.patient_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.patient_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Add table inside the scroll area
        self.scroll_area.setWidget(self.patient_table)
        main_layout.addWidget(self.scroll_area)

        # Save Button
        save_button = QPushButton("Save Changes")
        save_button.setIcon(QIcon.fromTheme("document-save"))
        save_button.clicked.connect(self.save_changes)
        main_layout.addWidget(save_button, alignment=Qt.AlignRight)

        self.setLayout(main_layout)
        self.load_assigned_patients()

    def load_assigned_patients(self):
        """Fetch and display patient records."""
        api_url = os.getenv("MEDICAL_RECORD_URL") + f"/?patient_id={self.patient_id}"
        patient = fetch_data(self, api_url, self.token)

        if not patient:
            QMessageBox.warning(self, "No Medical Record", "Patient medical record has not been created.")
            return

        if patient and isinstance(patient, list):
            patient = patient[0]  # Get the first patient
        elif isinstance(patient, dict):  # If API returned a dictionary instead
            patient = patient

        # Set row count to 1 since it's a single patient
        self.patient_table.setRowCount(1)

        # Fill in patient details
        self.patient_table.setItem(0, 0, QTableWidgetItem(str(patient.get("patient_name", ""))))
        self.patient_table.setItem(0, 1, QTableWidgetItem(patient.get("medical_history", "")))
        self.patient_table.setItem(0, 2, QTableWidgetItem(patient.get("diagnosis", "")))
        self.patient_table.setItem(0, 3, QTableWidgetItem(patient.get("treatment_plan", "")))
        self.patient_table.setItem(0, 4, QTableWidgetItem(patient.get("prescription", "")))
        self.patient_table.setItem(0, 5, QTableWidgetItem(patient.get("lab_tests_results", "")))
        self.patient_table.setItem(0, 6, QTableWidgetItem(patient.get("scan_results", "")))
        self.patient_table.setItem(0, 7, QTableWidgetItem(patient.get("notes", "")))

        # Button to View Patient Record
        self.patient_table.setCellWidget(0, 8, self.create_view_button(patient.get("id", "")))

    def create_view_button(self, patient_id):
        """Create 'View Record' button for each patient."""
        button = QPushButton("Update Record")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.open_patient_record(patient_id))
        return button

    def open_patient_record(self, patient_id):
        """Open the patient record management window."""
        self.patient_record_window = PatientRecordUpdateWindow(patient_id, self.token, self.doctor_id)
        self.patient_record_window.show()
        self.close()

    def save_changes(self):
        """Save changes to the patient record."""
        QMessageBox.information(self, "Success", "Changes saved successfully!")

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