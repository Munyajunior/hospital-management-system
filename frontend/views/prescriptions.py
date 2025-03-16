import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QHBoxLayout, QHeaderView, QScrollArea, QFormLayout, QLineEdit, QListWidget
)
from utils.api_utils import fetch_data, post_data
from PySide6.QtCore import Qt, Signal


class Prescriptions(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Prescription Management interface.

        :param user_role: Role of the logged-in user (doctor/nurse/pharmacist)
        :param user_id: ID of the logged-in user (for filtering prescriptions)
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.inventory = {}  # Store drug inventory
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Prescribe Medication")
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
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
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1e6fa7;
            }
            QComboBox, QTextEdit, QLineEdit, QListWidget {
                background-color: white;
                border: 1px solid #dcdcdc;
                font-size: 14px;
                padding: 8px;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel("Manage Prescriptions")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Scrollable Prescription Table
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(6)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Medication", "Dosage", "Instructions", "Status"])
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.scroll_area.setWidget(self.prescription_table)
        layout.addWidget(self.scroll_area)

        # Patient Selection
        self.patient_dropdown = QComboBox()
        self.patient_dropdown.setPlaceholderText("Select a Patient")
        self.load_patients()
        layout.addWidget(self.patient_dropdown)

        # Search Bar for Drugs
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a drug...")
        self.search_input.textChanged.connect(self.search_drugs)
        layout.addWidget(self.search_input)

        # List to Display Available Drugs
        self.drug_list = QListWidget()
        self.drug_list.itemClicked.connect(self.select_drug)
        layout.addWidget(self.drug_list)

        # Medication Input Fields
        form_layout = QFormLayout()

        self.medication_input = QLineEdit()
        self.medication_input.setPlaceholderText("Selected medications will appear here...")
        self.medication_input.setReadOnly(True)
        form_layout.addRow("Selected Medications:", self.medication_input)

        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("Enter dosage(s), comma-separated...")
        form_layout.addRow("Dosages:", self.dosage_input)

        self.instructions_input = QTextEdit()
        self.instructions_input.setPlaceholderText("Enter instructions...")
        form_layout.addRow("Instructions:", self.instructions_input)

        layout.addLayout(form_layout)

        # Button Layout
        button_layout = QHBoxLayout()

        self.prescribe_button = QPushButton("Prescribe Medication")
        self.prescribe_button.clicked.connect(self.prescribe_medication)
        button_layout.addWidget(self.prescribe_button)

        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        self.load_inventory()  # Load available drugs
        self.load_prescriptions()

        self.setLayout(layout)

    def load_patients(self):
        """Fetch and populate the dropdown with assigned patients."""
        base_url = os.getenv("ASSIGNED_PATIENTS_URL")
        api_url = f"{base_url}/{self.user_id}/patients"
        patients = fetch_data(self, api_url, self.token)

        if not patients:
            QMessageBox.information(self, "No Patients", "No patients assigned yet.")
            return

        for patient in patients:
            self.patient_dropdown.addItem(patient["full_name"], patient["id"])

    def load_inventory(self):
        """Fetches available drugs from inventory."""
        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory_data = fetch_data(self, api_url, self.token)

        if not inventory_data:
            QMessageBox.critical(self, "Error", "Failed to load inventory.")
            return

        self.inventory = {drug["drug_name"]: drug["quantity"] for drug in inventory_data}
        self.update_drug_list()  # Populate the drug list with all available drugs

    def update_drug_list(self, search_query=""):
        """Updates the drug list based on the search query."""
        self.drug_list.clear()
        for drug_name, quantity in self.inventory.items():
            if search_query.lower() in drug_name.lower():
                self.drug_list.addItem(f"{drug_name} ({quantity} in stock)")

    def search_drugs(self):
        """Filters the drug list based on the search query."""
        search_query = self.search_input.text().strip()
        self.update_drug_list(search_query)

    def select_drug(self, item):
        """Adds the selected drug to the medication input."""
        selected_drug = item.text().split(" (")[0]  # Extract drug name from the list item
        current_medications = self.medication_input.text().strip()
        if current_medications:
            self.medication_input.setText(f"{current_medications}, {selected_drug}")
        else:
            self.medication_input.setText(selected_drug)

    def load_prescriptions(self):
        """Fetch and display prescriptions."""
        api_url = os.getenv("PRESCRIPTIONS_URL")
        prescriptions = fetch_data(self, api_url, self.token)
        if not prescriptions:
            QMessageBox.information(self, "No Prescriptions", "No prescriptions available.")
            return
        self.populate_table(prescriptions)

    def populate_table(self, prescriptions):
        """Fills the table with prescription data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(str(prescription["patient_id"])))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(str(prescription["prescribed_by"])))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["drug_name"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["dosage"]))
            self.prescription_table.setItem(row, 4, QTableWidgetItem(prescription["instructions"]))
            self.prescription_table.setItem(row, 5, QTableWidgetItem(prescription["status"]))

    def prescribe_medication(self):
        """Validates and prescribes medication."""
        patient_id = self.patient_dropdown.currentData()
        medications = self.medication_input.text().strip().split(",")
        dosages = self.dosage_input.text().strip().split(",")
        instructions = self.instructions_input.toPlainText().strip()

        if not patient_id or not medications or not dosages or len(medications) != len(dosages):
            QMessageBox.warning(self, "Validation Error", "Ensure medication names and dosages are correctly entered.")
            return

        # Check if medications exist in inventory
        unavailable_drugs = [drug.strip() for drug in medications if drug.strip() not in self.inventory]

        if unavailable_drugs:
            QMessageBox.warning(self, "Out of Stock", f"The following drugs are not available: {', '.join(unavailable_drugs)}")
            return

        api_url = os.getenv("PRESCRIPTIONS_URL")
        for med, dose in zip(medications, dosages):
            data = {
                "prescribed_by": self.user_id,
                "patient_id": patient_id,
                "drug_name": med.strip(),
                "dosage": dose.strip(),
                "instructions": instructions
            }
            response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Medications prescribed successfully!")
            self.load_prescriptions()
            self.clear_fields()
        else:
            QMessageBox.critical(self, "Error", "Failed to prescribe medication.")

    def clear_fields(self):
        """Clears all input fields."""
        self.medication_input.clear()
        self.dosage_input.clear()
        self.instructions_input.clear()
        self.search_input.clear()
        self.update_drug_list()  # Reset the drug list