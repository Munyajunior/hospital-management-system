import os
from PySide6.QtWidgets import (QApplication,
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt
from utils.api_utils import fetch_data, post_data

class ICUManagement(QWidget):
    def __init__(self, user_role, user_id, auth_token):
        """
        Initializes the ICU & Critical Care Management interface.

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
        self.setWindowTitle("ICU & Critical Care Management")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(900, 600)  # Set a reasonable minimum size

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("ICU & Critical Care Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.title_label)

        # ICU Patient Table
        self.icu_table = QTableWidget()
        self.icu_table.setColumnCount(5)
        self.icu_table.setHorizontalHeaderLabels(["Patient", "Condition", "Assigned Doctor", "Bed Number", "Status"])
        self.icu_table.setStyleSheet("QTableWidget { font-size: 14px; }")
        layout.addWidget(self.icu_table)

        # Assign ICU Bed (Admin/Nurse Only)
        if self.user_role in ["admin", "nurse"]:
            form_layout = QVBoxLayout()

            self.patient_dropdown = QComboBox()
            self.load_patients()
            form_layout.addWidget(self.patient_dropdown)

            self.bed_number_input = QTextEdit()
            self.bed_number_input.setPlaceholderText("Enter ICU Bed Number...")
            form_layout.addWidget(self.bed_number_input)

            self.assign_bed_button = QPushButton("Assign ICU Bed")
            self.assign_bed_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
            self.assign_bed_button.clicked.connect(self.assign_icu_bed)
            form_layout.addWidget(self.assign_bed_button)

            layout.addLayout(form_layout)

        # ICU Monitoring (Doctor Only)
        if self.user_role == "doctor":
            self.monitor_button = QPushButton("View ICU Monitoring")
            self.monitor_button.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
            self.monitor_button.clicked.connect(self.view_icu_monitoring)
            layout.addWidget(self.monitor_button)

        # Load ICU Patients Button
        self.load_icu_button = QPushButton("Refresh ICU Patients")
        self.load_icu_button.clicked.connect(self.load_icu_patients)
        self.load_icu_button.setStyleSheet("background-color: #007bff; color: white; padding: 10px;")
        layout.addWidget(self.load_icu_button)

        self.load_icu_patients()
        self.setLayout(layout)

    def load_patients(self):
        """Fetches and populates the dropdown with patients."""
        if self.user_role not in ["admin", "nurse"]:
            return


        api_url = os.getenv("PATIENT_LIST_URL")
        patients = fetch_data(self, api_url, self.token)

        if patients:
            for patient in patients:
                self.patient_dropdown.addItem(patient["full_name"], patient["id"])
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch patient list.")
    def load_icu_patients(self):
        """Fetches and displays ICU patients."""

        api_url = os.getenv("GET_ICU_PATIENTS_URL")
        icu_patients = fetch_data(self, api_url, self.token)

        if icu_patients:
            self.populate_table(icu_patients)
        else:
                QMessageBox.critical(self, "Error", "Failed to fetch ICU patient list.")

    def populate_table(self, icu_patients):
        """Fills the ICU patient table with data."""
        self.icu_table.setRowCount(len(icu_patients))
        for row, patient in enumerate(icu_patients):
            self.icu_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
            self.icu_table.setItem(row, 1, QTableWidgetItem(patient["condition"]))
            self.icu_table.setItem(row, 2, QTableWidgetItem(patient["assigned_doctor"]))
            self.icu_table.setItem(row, 3, QTableWidgetItem(patient["bed_number"]))
            self.icu_table.setItem(row, 4, QTableWidgetItem(patient["status"]))

    def assign_icu_bed(self):
        """Allows an admin or nurse to assign a bed to a patient."""
        if self.user_role not in ["admin", "nurse"]:
            QMessageBox.warning(self, "Unauthorized", "Only admins and nurses can assign ICU beds.")
            return

        patient_id = self.patient_dropdown.currentData()
        bed_number = self.bed_number_input.toPlainText()

        if not patient_id or not bed_number:
            QMessageBox.warning(self, "Validation Error", "Please select a patient and enter a valid bed number.")
            return

        api_url = os.getenv("ASSIGN_ICU_BED_URL")
        data = {
            "patient_id": patient_id,
            "bed_number": bed_number,
            "assigned_by": self.user_id
        }
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "ICU bed assigned successfully.")
            self.load_icu_patients()
        else:
            QMessageBox.critical(self, "Error", "Failed to assign ICU bed.")

    def view_icu_monitoring(self):
        """Fetches and displays ICU monitoring data (for doctors)."""
        if self.user_role != "doctor":
            QMessageBox.warning(self, "Unauthorized", "Only doctors can view ICU monitoring.")
            return

        api_url = os.getenv("ICU_MONITORING_URL")
        monitoring_data = fetch_data(self, api_url, self.token)

        if monitoring_data:
            self.show_monitoring_popup(monitoring_data)
        else:
            QMessageBox.critical(self, "Error", "Failed to fetch ICU monitoring data.")

    def show_monitoring_popup(self, monitoring_data):
        """Displays ICU monitoring data in a popup window."""
        monitoring_text = "\n".join(
            [f"{item['patient_name']}: {item['vitals']}" for item in monitoring_data]
        )
        QMessageBox.information(self, "ICU Monitoring Data", monitoring_text)
