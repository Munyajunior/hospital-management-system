import os
import requests
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QTextEdit, QHeaderView
)
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, update_data


class LabTestManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the Lab Test Management interface.

        :param user_role: Role of the logged-in user (doctor/lab_technician/patient)
        :param user_id: ID of the logged-in user
        :param auth_token: Authentication token for API authorization
        """
        super().__init__()
        self.role = user_role
        self.user_id = user_id
        self.token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Laboratory Test Management")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #F4F6F7;
                font-family: Arial, sans-serif;
            }
        """)

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("Laboratory Test Requests")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2C3E50;
            padding: 15px;
        """)
        layout.addWidget(self.title_label)

        # Lab Test Requests Table
        self.lab_test_table = QTableWidget()
        self.lab_test_table.setColumnCount(7)
        self.lab_test_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Test Type", "Status", "Results", "Additional Notes", "Action" ])
        self.lab_test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lab_test_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #D5DBDB;
                font-size: 14px;
                alternate-background-color: #F8F9F9;
            }
            QHeaderView::section {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                padding: 5px;
                border: none;
            }
        """)
        layout.addWidget(self.lab_test_table)

    
        # Load Lab Tests Button
        self.load_lab_tests_button = QPushButton("Refresh Lab Test Requests")
        self.load_lab_tests_button.clicked.connect(self.load_lab_test_requests)
        self.load_lab_tests_button.setStyleSheet(self.button_style())
        layout.addWidget(self.load_lab_tests_button)

        self.load_lab_test_requests()
        self.setLayout(layout)

    def button_style(self, small=False):
        """Return a modern button style with hover effects."""
        size = "padding: 10px 20px;" if not small else "padding: 6px 12px;"
        return f"""
            QPushButton {{
                background-color: #007BFF;
                color: white;
                border-radius: 5px;
                {size}
                font-size: 14px;
                border: none;
                max-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
        """
    def load_lab_test_requests(self):
        """Fetches and displays lab test requests."""
        api_url = os.getenv("LAB_TESTS_URL")

        lab_tests = fetch_data(self, api_url, self.token)
        if lab_tests:
            self.populate_table(lab_tests)
        else:
            QMessageBox.information("Empty", "No lab test request have been made.")
            

    def populate_table(self, lab_tests):
        """Fills the lab test requests table with data."""
        self.lab_test_table.setRowCount(len(lab_tests))
        for row, request in enumerate(lab_tests):
            self.lab_test_table.setItem(row, 0, QTableWidgetItem(request["patient_name"]))
            self.lab_test_table.setItem(row, 1, QTableWidgetItem(request["requested_by"]))
            self.lab_test_table.setItem(row, 2, QTableWidgetItem(request["test_type"]))
            self.lab_test_table.setItem(row, 3, QTableWidgetItem(request["status"]))
            self.lab_test_table.setItem(row, 5, QTableWidgetItem(request["results"]))
            self.lab_test_table.setItem(row, 6, QTableWidgetItem(request.get("additional_notes", "")))

            self.lab_test_table.setCellWidget(row, 7, self.create_view_lab_button(request))
            
    def create_view_lab_button(self,request):
        """Creates the 'Process Lab' button."""
        button = QPushButton("🛠 Process Test")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.show_request_process(
            request["id"], request["patient_id"], request["requested_by"], request["test_type"], request["status"]
        ))
        return button
    
    def show_request_process(self, request_id, patient_id, requested_by, test_type, status):
        """Displays details of a Lab Test request and provides update options."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Lab Test Request Details")
        msg.setText(
            f"📌 Patient: {str(patient_id)}\n"
            f"🗓 Requested By: {str(requested_by)}\n"
            f"📄 Test Type: {test_type}\n"
            f"📄 Status: {status}\n\n"
            "Select an action below:\n\n"
            "Change status to 'In Progress' before processing the request."
        )

        in_progress_btn = msg.addButton("📝 In Progress", QMessageBox.ButtonRole.ActionRole)
        update_btn = msg.addButton("⏳ Update", QMessageBox.ButtonRole.ActionRole)
        close_btn = msg.addButton(QMessageBox.StandardButton.Close)

        msg.exec()

        if msg.clickedButton() == update_btn:
            self.update_scan_request(request_id)
        elif msg.clickedButton() == in_progress_btn:
            self.status_in_progress(request_id)
            
    def status_in_progress(self, test_id):
        """Updates the Lab Test request status to 'In Progress'."""
        base_url = os.getenv("LAB_TESTS_URL")
        api_url = f"{base_url}{test_id}/in-progress"

        data = {
            "status": "In Progress",
            "results": "Processing lab Test(s), please be patient..."
        }

        status = update_data(self, api_url, data, self.token)

        if not status:
            QMessageBox.warning(self, "Error", "Failed to update Lab Test status.")
            return

        self.load_lab_test_requests()
        QMessageBox.information(self, "Success", "Lab Test status updated to 'In Progress'.")

    def update_scan_request(self, test_id):
        """Opens the update scan window."""
        self.update_scan = UpdateRequestedLab(test_id, self.token)
        self.update_scan.show()
        self.load_lab_test_requests()


class UpdateRequestedLab(QWidget):
    def __init__(self, test_id, token):
        super().__init__()
        self.test_id = test_id
        self.token = token
        self.setWindowTitle("Update Radiology Scan")
        self.setGeometry(400, 250, 400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.results_input = QTextEdit()
        self.results_input.setPlaceholderText("Enter Results of Lab Tests")
        self.results_input.setStyleSheet("font-size: 14px; padding: 8px;")

        self.update_button = QPushButton("✅ Update Test")
        self.update_button.setStyleSheet("""
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        self.update_button.clicked.connect(self.update_test)

        layout.addWidget(self.results_input)
        layout.addWidget(self.update_button)
        self.setLayout(layout)

    def update_scan(self):
        """Handles Test update logic."""
        results = self.results_input.toPlainText().strip()
        if not results:
            QMessageBox.warning(self, "Error", "Results cannot be empty.")
            return

        api_url = f"{os.getenv('LAB_TESTS_URL')}{self.test_id}/update"
        data = {
            "status": "Completed",  
            "results": results 
        }

        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Scan updated successfully.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to update scan.")
