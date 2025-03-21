import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QLineEdit, QFormLayout, QHeaderView, QHBoxLayout, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor
from utils.api_utils import fetch_data, post_data


class Scans(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Scan Management interface.

        :param user_role: Role of the logged-in user (doctor/radiology_staff/patient)
        :param user_id: ID of the logged-in user (for filtering scan requests)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.current_theme = "light"  # Default theme

        if self.user_role in ["doctor", "admin"]:
            self.setWindowTitle("Scan Request")
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            max_width = screen_geometry.width() * 0.8  # 80% of screen width
            max_height = screen_geometry.height() * 0.8  # 80% of screen height

            self.resize(int(max_width), int(max_height))  # Set window size
            self.setMinimumSize(900, 600)  # Set a reasonable minimum size
            self.init_ui()
        else:
            QMessageBox.warning(self, "Unauthorized access", "You are not authorized to access this interface")
            return

    def init_ui(self):
        """Initialize UI elements with enhanced styling."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel("📡 Request Radiographic Scans")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            padding: 15px;
        """)
        layout.addWidget(self.title_label)

        # Search Bar and Theme Toggle
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by Patient ID, Scan Type, or Status...")
        self.search_input.textChanged.connect(self.filter_scans)
        search_layout.addWidget(self.search_input)

        # Theme Toggle Button
        self.theme_toggle_button = QPushButton("🌙 Toggle Theme")
        self.theme_toggle_button.setStyleSheet(self.button_style())
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        search_layout.addWidget(self.theme_toggle_button)

        layout.addLayout(search_layout)

        # Scan Requests Table
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(6)
        self.scan_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Scan Type", "Status", "Results", "Additional Notes"])
        self.scan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scan_table.setAlternatingRowColors(True)
        self.add_placeholder_header()  # Add placeholder header row
        layout.addWidget(self.scan_table)

        # Form Layout for Scan Request
        form_layout = QFormLayout()

        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        form_layout.addRow("Patient:", self.patient_dropdown)

        # Scan Type Input
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Enter scan type (e.g., X-Ray, MRI, CT Scan)...")
        form_layout.addRow("Scan Type:", self.scan_input)

        layout.addLayout(form_layout)

        # Button Layout
        button_layout = QHBoxLayout()

        # Button to Request Scan
        self.request_scan_button = QPushButton("📝 Request Scan")
        self.request_scan_button.setIcon(QIcon("assets/icons/add.png"))
        self.request_scan_button.clicked.connect(self.request_scan)
        self.request_scan_button.setStyleSheet(self.button_style())
        button_layout.addWidget(self.request_scan_button)

        # Button to Refresh Scans
        self.load_scans_button = QPushButton("🔄 Refresh Scan Requests")
        self.load_scans_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.load_scans_button.clicked.connect(self.load_scan_requests)
        self.load_scans_button.setStyleSheet(self.button_style())
        button_layout.addWidget(self.load_scans_button)

        layout.addLayout(button_layout)

        self.load_scan_requests()
        self.setLayout(layout)
        self.apply_theme(self.current_theme)  # Apply default theme

    def add_placeholder_header(self):
        """Add a placeholder row to simulate a duplicated header."""
        self.scan_table.insertRow(0)  # Insert a new row at the top
        for col in range(self.scan_table.columnCount()):
            header_text = self.scan_table.horizontalHeaderItem(col).text()  # Get header text
            item = QTableWidgetItem(header_text)  # Create a QTableWidgetItem with the header text
            item.setFlags(Qt.NoItemFlags)  # Make the placeholder row non-editable
            item.setBackground(QColor("#007BFF"))  # Set background color to match the header
            item.setForeground(QColor("white"))  # Set text color to white
            self.scan_table.setItem(0, col, item)  # Add the item to the table

    def apply_theme(self, theme):
        """Apply light or dark theme to the application."""
        self.current_theme = theme
        if theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #2C3E50;
                    color: #ECF0F1;
                }
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #ECF0F1;
                    padding: 10px;
                }
                QLineEdit, QComboBox {
                    background-color: #34495E;
                    color: #ECF0F1;
                    border: 1px solid #555;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                }
                QTableWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    alternate-background-color: #2C3E50;
                    border: 1px solid #555;
                    border-radius: 5px;
                }
                QHeaderView::section {
                    background-color: #007BFF;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border: none;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F4F6F7;
                    font-family: Arial, sans-serif;
                }
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    padding: 10px;
                }
                QLineEdit, QComboBox {
                    background-color: white;
                    border: 1px solid #D5DBDB;
                    font-size: 14px;
                    padding: 8px;
                    border-radius: 5px;
                }
                QTableWidget {
                    background-color: white;
                    border: 1px solid #D5DBDB;
                    font-size: 14px;
                    alternate-background-color: #F8F9F9;
                    border-radius: 5px;
                }
                QHeaderView::section {
                    background-color: #007BFF;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border: none;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

    def button_style(self):
        """Return CSS for the buttons."""
        return """
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #007BFF;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """

    def load_patients(self):
        """Fetches and populates the dropdown with assigned patients."""
        base_url = os.getenv("ASSIGNED_PATIENTS_URL")
        api_url = f"{base_url}/{self.user_id}/patients"
        patients = fetch_data(self, api_url, self.token)
        if patients:
            for patient in patients:
                self.patient_dropdown.addItem(patient["full_name"], patient["id"])
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch patients.")

    def load_scan_requests(self):
        """Fetches and displays scan requests."""
        base_url = os.getenv("SCANS_URL")
        api_url = f"{base_url}scan/{self.user_id}"
        scans = fetch_data(self, api_url, self.token)
        if scans:
            self.scans = scans  # Store scans for filtering
            self.populate_table(scans)
        else:
            QMessageBox.information(self, "No Scans", "No scan requests found.")

    def populate_table(self, scans):
        """Fills the table with scan data."""
        self.scan_table.setRowCount(0)  # Clear existing data
        self.add_placeholder_header()  # Add placeholder header row

        for row, scan in enumerate(scans):
            self.scan_table.insertRow(row + 1)  # Insert rows below the placeholder header
            self.scan_table.setItem(row + 1, 0, QTableWidgetItem(str(scan["patient_id"])))
            self.scan_table.setItem(row + 1, 1, QTableWidgetItem(str(scan["requested_by"])))
            self.scan_table.setItem(row + 1, 2, QTableWidgetItem(scan["scan_type"]))
            self.scan_table.setItem(row + 1, 3, QTableWidgetItem(scan["status"]))
            if scan["status"] == "Completed":
                self.scan_table.setItem(row + 1, 4, QTableWidgetItem(scan["results"]))
                self.scan_table.setItem(row + 1, 5, QTableWidgetItem(scan["additional_notes"]))

    def filter_scans(self):
        """Filters scan requests based on the search query."""
        query = self.search_input.text().strip().lower()
        if not query:
            self.populate_table(self.scans)
            return

        filtered_scans = [
            scan for scan in self.scans
            if (query in str(scan["patient_id"]).lower() or
                query in scan["scan_type"].lower() or
                query in scan["status"].lower())
        ]
        self.populate_table(filtered_scans)

    def request_scan(self):
        """Submits a scan request for a patient."""
        patient_id = int(self.patient_dropdown.currentData())
        scan_type = self.scan_input.text().strip()
        requested_by = int(self.user_id)

        if not patient_id or not scan_type:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        data = {
            "patient_id": patient_id,
            "scan_type": scan_type,
            "requested_by": requested_by
        }
        api_url = os.getenv("SCANS_URL")
        response = post_data(self, api_url, data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Scan requested successfully!")
            self.load_scan_requests()
        else:
            QMessageBox.warning(self, "Error", "Failed to request scan.")