from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView,
    QMessageBox, QLineEdit, QHeaderView, QDialog, QTextEdit, QStyledItemDelegate, QStyleOptionButton, QStyle
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QMouseEvent, QColor
from utils.api_utils import fetch_data, update_data
import os


class ButtonDelegate(QStyledItemDelegate):
    """Custom delegate to render a button in the table view."""
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Render the button only for data rows (skip the placeholder header row)
        if index.row() != 0:  # Skip the first row (placeholder header)
            button_style = QStyleOptionButton()
            button_style.rect = option.rect
            button_style.text = "🛠 Process Test"
            button_style.state = QStyle.State_Enabled | QStyle.State_Active
            QApplication.style().drawControl(QStyle.CE_PushButton, button_style, painter)

    def editorEvent(self, event, model, option, index):
        # Handle button click only for data rows (skip the placeholder header row)
        if index.row() != 0 and event.type() == QMouseEvent.MouseButtonRelease:
            self.parent().process_button_clicked(index)
            return True
        return False


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
        self.settings = QSettings("MyOrg", "LabTestManagement")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Laboratory Test Management")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(900, 600)  # Set a reasonable minimum size

        # Apply dark or light theme based on system or user preference
        self.apply_theme(self.settings.value("theme", "light"))

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Title
        self.title_label = QLabel("Laboratory Test Requests")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
        """)
        main_layout.addWidget(self.title_label)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by Patient, Doctor, or Test Type...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_table)  # Connect to filter function
        main_layout.addWidget(self.search_bar)

        # Lab Test Requests Table
        self.lab_test_table = QTableView()
        self.lab_test_table.setStyleSheet("""
            QTableView {
                font-size: 14px;
                alternate-background-color: #F8F9F9;
            }
            QHeaderView::section {
                font-weight: bold;
                padding: 5px;
                border: none;
            }
        """)
        self.lab_test_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Create a model for the table
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Patient", "Doctor", "Test Type", "Status", "Results", "Additional Notes", "Action"])
        self.lab_test_table.setModel(self.model)

        # Set custom delegate for the "Action" column
        self.button_delegate = ButtonDelegate(self)
        self.lab_test_table.setItemDelegateForColumn(6, self.button_delegate)

        # Add a placeholder row to simulate a duplicated header
        self.add_placeholder_header()

        main_layout.addWidget(self.lab_test_table)

        # Button Layout
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        # Load Lab Tests Button
        self.load_lab_tests_button = QPushButton("Refresh Lab Test Requests")
        self.load_lab_tests_button.clicked.connect(self.load_lab_test_requests)
        self.load_lab_tests_button.setIcon(QIcon("assets/icons/refresh.png"))
        self.load_lab_tests_button.setStyleSheet(self.button_style())
        button_layout.addWidget(self.load_lab_tests_button)

        # Theme Toggle Button
        self.theme_toggle_button = QPushButton("Toggle Dark/Light Mode")
        self.theme_toggle_button.clicked.connect(self.toggle_theme)
        self.theme_toggle_button.setStyleSheet(self.button_style())
        button_layout.addWidget(self.theme_toggle_button)

        self.load_lab_test_requests()

    def apply_theme(self, theme):
        """Apply dark or light theme to the application."""
        if theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #2C3E50;
                    color: #ECF0F1;
                }
                QTableView {
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
                    color: #ECF0F1;
                    border: 1px solid #555;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #F4F6F7;
                    color: #2C3E50;
                }
                QTableView {
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
                    border: 1px solid #ccc;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                }
            """)

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        current_theme = self.settings.value("theme", "light")
        new_theme = "dark" if current_theme == "light" else "light"
        self.settings.setValue("theme", new_theme)
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

    def filter_table(self):
        """Filters the table rows based on the search query."""
        search_text = self.search_bar.text().strip().lower()
        for row in range(self.model.rowCount()):
            match = False
            for col in range(self.model.columnCount() - 1):  # Exclude the "Action" column
                item = self.model.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.lab_test_table.setRowHidden(row, not match)

    def load_lab_test_requests(self):
        """Fetches and displays lab test requests."""
        api_url = os.getenv("LAB_TESTS_URL")

        lab_tests = fetch_data(self, api_url, self.token)
        if lab_tests:
            self.populate_table(lab_tests)
        else:
            QMessageBox.information(self, "Empty", "No lab test requests have been made.")

    def add_placeholder_header(self):
        """Add a placeholder row to simulate a duplicated header."""
        placeholder_row = []
        for col in range(self.model.columnCount()):  # Iterate over each column
            header_text = self.model.horizontalHeaderItem(col).text()  # Get header text
            item = QStandardItem(header_text)  # Create a QStandardItem with the header text
            item.setFlags(Qt.NoItemFlags)  # Make the placeholder row non-editable
            item.setBackground(QColor("#007BFF"))  # Set background color to match the header
            item.setForeground(QColor("white"))  # Set text color to white
            placeholder_row.append(item)  # Add the item to the row
        self.model.appendRow(placeholder_row)  # Add the row to the model

    def populate_table(self, lab_tests):
        """Fills the lab test requests table with data."""
        self.model.clear()  # Clear existing data
        self.model.setHorizontalHeaderLabels(["Patient", "Doctor", "Test Type", "Status", "Results", "Additional Notes", "Action"])

        # Add the placeholder header row
        self.add_placeholder_header()

        # Populate the table with data
        for request in lab_tests:
            row = [
                QStandardItem(str(request["patient_id"])),
                QStandardItem(str(request["requested_by"])),
                QStandardItem(request["test_type"]),
                QStandardItem(request["status"]),
                QStandardItem(request["results"]),
                QStandardItem(request.get("additional_notes", "")),
                QStandardItem("🛠 Process Test")  # Placeholder for action
            ]
            self.model.appendRow(row)

    def process_button_clicked(self, index):
        """Handle button click in the 'Action' column."""
        request_id = self.model.item(index.row(), 0).text()  # Get request ID from the first column
        patient_id = self.model.item(index.row(), 0).text()
        requested_by = self.model.item(index.row(), 1).text()
        test_type = self.model.item(index.row(), 2).text()
        status = self.model.item(index.row(), 3).text()
        self.show_request_process(request_id, patient_id, requested_by, test_type, status)

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
        self.update_scan.exec()  # Show as a modal dialog


class UpdateRequestedLab(QDialog):  # Changed to QDialog
    def __init__(self, test_id, token):
        super().__init__()
        self.test_id = test_id
        self.token = token
        self.setWindowTitle("Update Lab Test")
        self.setModal(True)  # Make the dialog modal
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.results_input = QTextEdit()
        self.results_input.setPlaceholderText("Enter Results of Lab Tests")
        self.results_input.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(self.results_input)

        self.update_button = QPushButton("✅ Update Test")
        self.update_button.setStyleSheet("""
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
        """)
        self.update_button.clicked.connect(self.update_test)
        layout.addWidget(self.update_button)

    def update_test(self):
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
            QMessageBox.information(self, "Success", "Lab Test updated successfully.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to update Lab Test.")