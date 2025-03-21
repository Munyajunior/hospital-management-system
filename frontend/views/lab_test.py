import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QLineEdit, QTextEdit, QHeaderView, QFormLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor
from utils.api_utils import fetch_data, post_data


class LabTests(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Lab Test Management interface.

        :param user_role: Role of the logged-in user (doctor/lab_staff/patient)
        :param user_id: ID of the logged-in user (for filtering test requests)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.current_theme = "light"  # Default theme
        if self.user_role in ["doctor", "admin"]:
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
        self.setWindowTitle("Request Lab Test")
        self.apply_theme(self.current_theme)  # Apply default theme

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel("🔬 Request Lab Tests")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            padding: 15px;
        """)
        layout.addWidget(self.title_label)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by Patient ID, Test Type, or Status...")
        self.search_input.textChanged.connect(self.filter_lab_tests)
        search_layout.addWidget(self.search_input)

        # Theme Toggle Button
        self.theme_toggle_button = QPushButton("🌙 Toggle Theme")
        self.theme_toggle_button.setStyleSheet(self.button_style())
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        search_layout.addWidget(self.theme_toggle_button)

        layout.addLayout(search_layout)

        # Lab Test Requests Table
        self.lab_test_table = QTableWidget()
        self.lab_test_table.setColumnCount(5)
        self.lab_test_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Test Type", "Status", "Additional Notes"])
        self.lab_test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.add_placeholder_header()  # Add placeholder header row
        layout.addWidget(self.lab_test_table)

        # Form Layout for Lab Test Request
        form_layout = QFormLayout()

        # Dropdown to select a patient
        self.patient_dropdown = QComboBox()
        self.load_patients()
        form_layout.addRow("Patient:", self.patient_dropdown)

        # Lab Test Input
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Enter lab test type (e.g., Blood Test)...")
        form_layout.addRow("Test Type:", self.test_input)

        # Additional Notes
        self.additional_input = QTextEdit()
        self.additional_input.setPlaceholderText("Enter additional notes...")
        form_layout.addRow("Additional Notes:", self.additional_input)

        layout.addLayout(form_layout)

        # Button Layout
        button_layout = QHBoxLayout()

        # Button to Request Lab Test
        self.request_test_button = QPushButton("📝 Request Lab Test")
        self.request_test_button.setIcon(QIcon("assets/icons/add.png"))
        self.request_test_button.clicked.connect(self.request_lab_test)
        self.request_test_button.setStyleSheet(self.button_style())
        button_layout.addWidget(self.request_test_button)

        # Button to Refresh Lab Tests
        self.load_test_button = QPushButton("🔄 Refresh Lab Tests")
        self.load_test_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.load_test_button.clicked.connect(self.load_lab_tests)
        self.load_test_button.setStyleSheet(self.button_style())
        button_layout.addWidget(self.load_test_button)

        layout.addLayout(button_layout)

        self.load_lab_tests()
        self.setLayout(layout)

    def add_placeholder_header(self):
        """Add a placeholder row to simulate a duplicated header."""
        self.lab_test_table.insertRow(0)  # Insert a new row at the top
        for col in range(self.lab_test_table.columnCount()):
            header_text = self.lab_test_table.horizontalHeaderItem(col).text()  # Get header text
            item = QTableWidgetItem(header_text)  # Create a QTableWidgetItem with the header text
            item.setFlags(Qt.NoItemFlags)  # Make the placeholder row non-editable
            item.setBackground(QColor("#007BFF"))  # Set background color to match the header
            item.setForeground(QColor("white"))  # Set text color to white
            self.lab_test_table.setItem(0, col, item)  # Add the item to the table

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
                    background-color: #2C3E50;
                    color: #ECF0F1;
                    padding: 10px;
                }
                QLineEdit, QTextEdit, QComboBox {
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
                QLineEdit, QTextEdit, QComboBox {
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

    def load_lab_tests(self):
        """Fetches and displays lab test requests."""
        base_url = os.getenv("LAB_TESTS_URL")
        api_url = f"{base_url}test/{self.user_id}"
        lab_tests = fetch_data(self, api_url, self.token)
        if lab_tests:
            self.lab_tests = lab_tests  # Store lab tests for filtering
            self.populate_table(lab_tests)

    def populate_table(self, lab_tests):
        """Fills the table with lab test data."""
        self.lab_test_table.setRowCount(0)  # Clear existing data
        self.add_placeholder_header()  # Add placeholder header row

        for row, lab_test in enumerate(lab_tests):
            self.lab_test_table.insertRow(row + 1)  # Insert rows below the placeholder header
            self.lab_test_table.setItem(row + 1, 0, QTableWidgetItem(str(lab_test["patient_id"])))
            self.lab_test_table.setItem(row + 1, 1, QTableWidgetItem(str(lab_test["requested_by"])))
            self.lab_test_table.setItem(row + 1, 2, QTableWidgetItem(lab_test["test_type"]))
            self.lab_test_table.setItem(row + 1, 3, QTableWidgetItem(lab_test["status"]))
            self.lab_test_table.setItem(row + 1, 4, QTableWidgetItem(lab_test.get("additional_notes", "")))

    def filter_lab_tests(self):
        """Filters lab test requests based on the search query."""
        query = self.search_input.text().strip().lower()
        if not query:
            self.populate_table(self.lab_tests)
            return

        filtered_tests = [
            test for test in self.lab_tests
            if (query in str(test["patient_id"]).lower() or
                query in test["test_type"].lower() or
                query in test["status"].lower())
        ]
        self.populate_table(filtered_tests)

    def request_lab_test(self):
        """Submits a lab test request for a patient."""
        patient_id = self.patient_dropdown.currentData()
        test_type = self.test_input.text().strip()
        additional_notes = self.additional_input.toPlainText().strip()

        if not patient_id or not test_type:
            QMessageBox.warning(self, "Validation Error", "Please provide all required fields.")
            return

        api_url = os.getenv("LAB_TEST_REQUEST_URL")
        data = {
            "requested_by": self.user_id,
            "patient_id": patient_id,
            "test_type": test_type,
            "additional_notes": additional_notes
        }

        lab_test = post_data(self, api_url, data, self.token)
        if lab_test:
            QMessageBox.information(self, "Success", "Lab test requested successfully!")
            self.load_lab_tests()  # Refresh the table
            self.test_input.clear()
            self.additional_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to request lab test.")