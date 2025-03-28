from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QApplication,
    QPushButton, QTextEdit, QMessageBox, QHBoxLayout, QLineEdit, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, update_data
import os


class RadiologyManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """Initializes the Radiology Management UI."""
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = auth_token
        self.is_dark_theme = False  # Track theme state
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Radiology & Scan Requests")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height

        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(950, 600)  # Set a reasonable minimum size

        self.layout = QVBoxLayout()
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Title and Theme Toggle
        title_layout = QHBoxLayout()
        self.title_label = QLabel("📡 Radiology & Scan Management")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(self.title_label)

        # Initialize the theme toggle button
        self.toggle_theme_button = QPushButton("🌙 Dark Theme")
        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        title_layout.addWidget(self.toggle_theme_button)
        self.layout.addLayout(title_layout)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by Patient ID, Scan Type, or Status...")
        self.search_input.textChanged.connect(self.filter_scan_requests)
        search_layout.addWidget(self.search_input)
        self.layout.addLayout(search_layout)

        # Scan Requests Table
        self.scan_table = QTableWidget()
        self.scan_table.setColumnCount(8)
        self.scan_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scan_table.setHorizontalHeaderLabels(
            ["ID", "Patient", "Requested By", "Scan Type", "Status", "Results", "Notes", "Actions"]
        )
        self.scan_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.scan_table, stretch=1)

        # Add a duplicate header at the bottom of the table
        self.duplicate_header()

        # Load Scan Requests Button
        self.load_scans_button = QPushButton("🔄 Load Requested Scans")
        self.load_scans_button.clicked.connect(self.load_scan_requests)
        self.layout.addWidget(self.load_scans_button)

        # Apply the initial theme after all UI elements are initialized
        self.apply_theme()

        self.load_scan_requests()
        self.setLayout(self.layout)

    def duplicate_header(self):
        """Adds a duplicate header at the bottom of the table."""
        self.scan_table.setRowCount(self.scan_table.rowCount() + 1)
        for col in range(self.scan_table.columnCount()):
            item = QTableWidgetItem(self.scan_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.scan_table.setItem(self.scan_table.rowCount() - 1, col, item)

    def load_scan_requests(self):
        """Fetches and displays scan requests."""
        api_url = os.getenv("SCANS_URL")
        scan_requests = fetch_data(self, api_url, self.token)
        if not scan_requests:
            QMessageBox.information(self, "No Requests", "No scan requests have been made.")
            return
        self.scan_requests = scan_requests  # Store scan requests for filtering
        self.populate_table(scan_requests)

    def populate_table(self, scan_requests):
        """Fills the scan requests table with data."""
        # Clear the table and add a row for the duplicate header
        self.scan_table.setRowCount(0)  # Clear all rows
        self.scan_table.insertRow(0)  # Insert a new row at the top for the duplicate header

        # Add the duplicate header at row 0
        for col in range(self.scan_table.columnCount()):
            item = QTableWidgetItem(self.scan_table.horizontalHeaderItem(col).text())
            item.setBackground(Qt.gray)
            item.setForeground(Qt.white)
            self.scan_table.setItem(0, col, item)

        # Populate the table with data starting from row 1
        for row, request in enumerate(scan_requests, start=1):  # Start from row 1
            self.scan_table.insertRow(row)  # Insert a new row for each request
            self.scan_table.setItem(row, 0, QTableWidgetItem(str(request["id"])))
            self.scan_table.setItem(row, 1, QTableWidgetItem(str(request["patient_id"])))
            self.scan_table.setItem(row, 2, QTableWidgetItem(str(request["requested_by"])))
            self.scan_table.setItem(row, 3, QTableWidgetItem(request["scan_type"]))
            self.scan_table.setItem(row, 4, QTableWidgetItem(request["status"]))
            self.scan_table.setItem(row, 5, QTableWidgetItem(request.get("results", "Pending")))
            self.scan_table.setItem(row, 6, QTableWidgetItem(request.get("additional_notes", "")))

            # Create "Process Scan" button for each request
            self.scan_table.setCellWidget(row, 7, self.create_view_record_button(request))
    def create_view_record_button(self, request):
        """Creates the 'Process Scan' button."""
        button = QPushButton("🛠 Process Scan")
        button.setStyleSheet(self.button_style(small=True))
        button.clicked.connect(lambda: self.show_request_process(
            request["id"], request["patient_id"], request["requested_by"], request["scan_type"], request["status"]
        ))
        return button

    def show_request_process(self, request_id, patient_id, requested_by, scan_type, status):
        """Displays details of a scan request and provides update options."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Scan Request Details")
        msg.setText(
            f"📌 Patient: {str(patient_id)}\n"
            f"🗓 Requested By: {str(requested_by)}\n"
            f"📄 Scan Type: {scan_type}\n"
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

    def filter_scan_requests(self):
        """Filters scan requests based on the search query."""
        query = self.search_input.text().strip().lower()
        if not query:
            self.populate_table(self.scan_requests)
            return

        filtered_requests = [
            req for req in self.scan_requests
            if (query in str(req["patient_id"]).lower() or
                query in req["scan_type"].lower() or
                query in req["status"].lower())
        ]
        self.populate_table(filtered_requests)

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

    def status_in_progress(self, scan_id):
        """Updates the scan request status to 'In Progress'."""
        base_url = os.getenv("SCANS_URL")
        api_url = f"{base_url}{scan_id}/in-progress"

        data = {
            "status": "In Progress",
            "results": "Processing scan, please be patient..."
        }

        status = update_data(self, api_url, data, self.token)

        if not status:
            QMessageBox.warning(self, "Error", "Failed to update scan status.")
            return

        self.load_scan_requests()
        QMessageBox.information(self, "Success", "Scan status updated to 'In Progress'.")

    def update_scan_request(self, scan_id):
        """Opens the update scan window."""
        self.update_scan = UpdateRequestedScan(scan_id, self.token)
        self.update_scan.show()
        
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
                }
                QTableWidget {
                    background-color: #34495E;
                    color: #ECF0F1;
                    alternate-background-color: #2C3E50;
                }
                QHeaderView::section {
                    background-color: #007BFF;
                    color: white;
                }
                QLineEdit {
                    background-color: #34495E;
                    font-size:14px;
                    color: #ECF0F1;
                    border: 1px solid #5D6D7E;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.toggle_theme_button.setText("☀️ Light Theme")
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F4F6F7;
                    color: #2C3E50;
                }
                QTableWidget {
                    background-color: white;
                    color: #2C3E50;
                    alternate-background-color: #F8F9F9;
                }
                QHeaderView::section {
                    background-color: #007BFF;
                    color: white;
                }
                QLineEdit {
                    background-color: white;
                    color: #2C3E50;
                    border: 1px solid #D5DBDB;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            self.toggle_theme_button.setText("🌙 Dark Theme")


class UpdateRequestedScan(QWidget):
    def __init__(self, scan_id, token):
        super().__init__()
        self.scan_id = scan_id
        self.token = token
        self.setWindowTitle("Update Radiology Scan")
        self.setGeometry(400, 250, 400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.results_input = QTextEdit()
        self.results_input.setPlaceholderText("Enter Results of Scan")
        self.results_input.setStyleSheet("font-size: 14px; padding: 8px;")

        self.update_button = QPushButton("✅ Update Scan")
        self.update_button.setStyleSheet("""
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        self.update_button.clicked.connect(self.update_scan)

        layout.addWidget(self.results_input)
        layout.addWidget(self.update_button)
        self.setLayout(layout)

    def update_scan(self):
        """Handles scan update logic."""
        results = self.results_input.toPlainText().strip()
        if not results:
            QMessageBox.warning(self, "Error", "Results cannot be empty.")
            return

        api_url = f"{os.getenv('SCANS_URL')}{self.scan_id}/update"
        data = {
            "status": "Completed",
            "results": results
        }

        response = update_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Scan updated successfully.")            
            self.load_scan_requests()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to update scan.")