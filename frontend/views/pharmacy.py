import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QDialog, QHeaderView, QTabWidget, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QFont
from utils.api_utils import fetch_data, post_data, update_data, delete_data


class Pharmacy(QWidget):
    def __init__(self, user_role, user_id, token):
        """
        Initializes the Pharmacy Management interface.

        :param user_role: Role of the logged-in user (doctor/pharmacy/patient)
        :param user_id: ID of the logged-in user
        :param token: Authentication token for API authorization
        """
        super().__init__()
        self.user_role = user_role
        self.user_id = user_id
        self.token = token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pharmacy Management")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel("Pharmacy & Medication Management")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        main_layout.addWidget(self.title_label)

        # Tab Widget for Prescriptions and Inventory
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 10px; }")

        # Prescription Tab
        self.prescription_tab = QWidget()
        self.init_prescription_tab()
        self.tabs.addTab(self.prescription_tab, "Prescriptions")

        # Inventory Tab (Pharmacist Only)
        if self.user_role == "pharmacist":
            self.inventory_tab = QWidget()
            self.init_inventory_tab()
            self.tabs.addTab(self.inventory_tab, "Inventory")
            
            # new tab for managing drug categories
            self.categories_tab = QWidget()
            self.init_categories_tab()
            self.tabs.addTab(self.categories_tab, "Categories")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def init_prescription_tab(self):
        """Initializes the Prescription tab."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Prescription Requests Table
        self.prescription_table = QTableWidget()
        self.prescription_table.setColumnCount(7)
        self.prescription_table.setHorizontalHeaderLabels(["Patient", "Doctor", "Medication", "Dosage", "Instructions", "Status", "Action"])
        self.prescription_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prescription_table.verticalHeader().setVisible(False)
        layout.addWidget(self.prescription_table)

        # Load Prescriptions Button
        self.load_prescriptions_button = QPushButton("Refresh Prescriptions")
        self.load_prescriptions_button.clicked.connect(self.load_prescriptions)
        layout.addWidget(self.load_prescriptions_button)

        self.prescription_tab.setLayout(layout)
        self.load_prescriptions()
    
    
    def load_prescriptions(self):
        """Fetches and displays prescription requests."""
        api_url = os.getenv("PRESCRIPTIONS_URL")
        prescriptions = fetch_data(self, api_url, self.token)
        
        if not prescriptions:
            QMessageBox.information(self, "No Prescriptions", "No drugs prescribed at the moment")
            return
        
        self.populate_table(prescriptions)

    def populate_table(self, prescriptions):
        """Fills the prescription table with data."""
        self.prescription_table.setRowCount(len(prescriptions))
        for row, prescription in enumerate(prescriptions):
            self.prescription_table.setItem(row, 0, QTableWidgetItem(str(prescription["patient_id"])))
            self.prescription_table.setItem(row, 1, QTableWidgetItem(str(prescription["prescribed_by"])))
            self.prescription_table.setItem(row, 2, QTableWidgetItem(prescription["drug_name"]))
            self.prescription_table.setItem(row, 3, QTableWidgetItem(prescription["dosage"]))
            self.prescription_table.setItem(row, 4, QTableWidgetItem(prescription["instructions"]))
            self.prescription_table.setItem(row, 5, QTableWidgetItem(prescription["status"]))

            # Dispense Button
            dispense_button = QPushButton("Dispense")
            dispense_button.setStyleSheet("background-color: #28a745; color: white; padding: 5px;")
            dispense_button.clicked.connect(lambda _, pid=prescription["id"], drug=prescription["drug_name"]: self.dispense_prescription(pid, drug))
            self.prescription_table.setCellWidget(row, 6, dispense_button)

    def dispense_prescription(self, prescription_id, drug_name):
        """Dispenses medication and updates stock and prescription status."""
        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory = fetch_data(self, api_url, self.token)
        if not inventory:
            QMessageBox.warning(self, "Inventory Error", "No inventory records found.")
            return
        
        # Find the drug in inventory
        drug_item = next((item for item in inventory if item["drug_name"].lower() == drug_name.lower()), None)
        if not drug_item:
            QMessageBox.warning(self, "Stock Error", f"'{drug_name}' is not available in inventory.")
            return

        if drug_item["quantity"] <= 0:
            QMessageBox.critical(self, "Out of Stock", f"'{drug_name}' is out of stock. Cannot dispense.")
            return

        # Update the inventory quantity
        new_quantity = drug_item["quantity"] - 1
        update_url = f"{api_url}{drug_item['id']}/update-quantity"
        inventory_update_data = {"quantity": new_quantity}
        inventory_updated = update_data(self, update_url, inventory_update_data, self.token)

        if not inventory_updated:
            QMessageBox.critical(self, "Update Error", "Failed to update inventory. Please try again.")
            return

        # Update the prescription status
        prescription_update_url = f"{os.getenv('PRESCRIPTIONS_URL')}{prescription_id}/dispense"
        prescription_update_data = {"status": "Dispensed"}
        prescription_updated = update_data(self, prescription_update_url, prescription_update_data, self.token)

        if prescription_updated:
            QMessageBox.information(self, "Success", f"'{drug_name}' has been dispensed successfully!")
            self.load_prescriptions()
            self.load_inventory()
        else:
            QMessageBox.critical(self, "Error", "Failed to update prescription status.")  
            
             
    def init_inventory_tab(self):
        """Initializes the Inventory tab."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Inventory Table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)  # Added a column for Category
        self.inventory_table.setHorizontalHeaderLabels(
            ["Medication", "Quantity", "Category", "Availability", "Update", "Delete"]
        )
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.verticalHeader().setVisible(False)
        layout.addWidget(self.inventory_table)

        # Add Inventory Form
        form_layout = QFormLayout()
        self.drug_name_input = QLineEdit()
        self.drug_name_input.setPlaceholderText("Enter drug name")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Enter quantity")
        self.quantity_input.setValidator(QIntValidator(0, 1000000))

        # Dropdown for selecting drug category
        self.category_dropdown = QComboBox()
        self.load_categories()  # Load categories into the dropdown
        form_layout.addRow("Drug Name:", self.drug_name_input)
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Category:", self.category_dropdown)

        self.add_inventory_button = QPushButton("Add to Inventory")
        self.add_inventory_button.clicked.connect(self.add_to_inventory)
        layout.addLayout(form_layout)
        layout.addWidget(self.add_inventory_button)

        # Load Inventory Button
        self.load_inventory_button = QPushButton("Refresh Inventory")
        self.load_inventory_button.clicked.connect(self.load_inventory)
        layout.addWidget(self.load_inventory_button)

        self.inventory_tab.setLayout(layout)
        self.load_inventory()

   
    def load_inventory(self):
        """Fetches and displays pharmacy inventory."""
        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory = fetch_data(self, api_url, self.token)
        if not inventory:
            QMessageBox.information(self, "No Inventory", "Please add inventory")
            return
        self.populate_inventory_table(inventory)

    def populate_inventory_table(self, inventory):
        """Fills the inventory table with data and adds update/delete buttons."""
        self.inventory_table.setRowCount(len(inventory))
        for row, item in enumerate(inventory):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item["drug_name"]))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(item["category"]["name"]))  # Display category name
            availability = "In Stock" if item["quantity"] > 0 else "Out of Stock"
            self.inventory_table.setItem(row, 3, QTableWidgetItem(availability))

            # Update Button
            update_button = QPushButton("Update")
            update_button.setStyleSheet("background-color: #ffc107; color: black; padding: 5px;")
            update_button.clicked.connect(lambda _, idx=item["id"]: self.update_inventory_item(idx))
            self.inventory_table.setCellWidget(row, 4, update_button)

            # Delete Button
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: #dc3545; color: white; padding: 5px;")
            delete_button.clicked.connect(lambda _, idx=item["id"]: self.delete_inventory_item(idx))
            self.inventory_table.setCellWidget(row, 5, delete_button)

    
    def update_inventory_item(self, item_id):
        """Opens a dialog to update an inventory item."""
        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        inventory = fetch_data(self, api_url, self.token)
        if not inventory:
            QMessageBox.warning(self, "Error", "Unable to fetch inventory data.")
            return

        # Find the item to update
        item_to_update = next((item for item in inventory if item["id"] == item_id), None)
        if not item_to_update:
            QMessageBox.warning(self, "Error", "Item not found in inventory.")
            return

        # Create a dialog for updating the item
        dialog = QDialog(self)  
        dialog.setWindowTitle("Update Inventory Item")
        dialog.setMinimumWidth(300)
        dialog_layout = QFormLayout()

        # Input fields
        drug_name_input = QLineEdit(item_to_update["drug_name"])
        quantity_input = QLineEdit(str(item_to_update["quantity"]))
        quantity_input.setValidator(QIntValidator(0, 1000000))
        self.category_dropdown = QComboBox()
        self.load_categories() 
        

        dialog_layout.addRow("Drug Name:", drug_name_input)
        dialog_layout.addRow("Quantity:", quantity_input)
        dialog_layout.addRow("Category:", self.category_dropdown)


        # Save Button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(lambda: self.save_updated_item(
            item_id, drug_name_input.text().strip(), quantity_input.text().strip(), self.category_dropdown.currentData(), dialog
        ))
        dialog_layout.addRow(save_button)

        # Cancel Button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.close)
        dialog_layout.addRow(cancel_button)

        dialog.setLayout(dialog_layout)
        dialog.exec_()
        
    

    def save_updated_item(self, item_id, drug_name, quantity, category, dialog):
        """Saves the updated inventory item."""
        if not drug_name or not quantity:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        update_url = f"{api_url}{item_id}"
        _data = {"drug_name": drug_name, "quantity": int(quantity), "category_id": int(category)}

        response = update_data(self, update_url, _data, self.token)
        if response:
            QMessageBox.information(self, "Success", "Inventory item updated successfully!")
            self.load_inventory()
            dialog.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to update inventory item.")

    def delete_inventory_item(self, item_id):
        """Deletes an inventory item."""
        confirm = QMessageBox.question(
            self, "Confirm Deletion", "Are you sure you want to delete this item?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        delete_url = f"{api_url}{item_id}"
        response = delete_data(self, delete_url, self.token)

        if response:
            QMessageBox.information(self, "Success", "Inventory item deleted successfully!")
            self.load_inventory()
        else:
            QMessageBox.critical(self, "Error", "Failed to delete inventory item.")
            
   
    def add_to_inventory(self):
        """Adds a new drug to the inventory."""
        drug_name = self.drug_name_input.text().strip()
        quantity = self.quantity_input.text().strip()
        category_id = self.category_dropdown.currentData()  # Get selected category ID
        added_by = self.user_id

        if not drug_name or not quantity or not category_id:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        api_url = os.getenv("PHARMACY_INVENTORY_URL")
        data = {"drug_name": drug_name, "quantity": int(quantity), "category_id": category_id, "added_by": added_by}
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Drug added to inventory!")
            self.load_inventory()
            self.drug_name_input.clear()
            self.quantity_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to add drug.")
            
    
    
    def init_categories_tab(self):
        """Initializes the Categories tab."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Add Category Form
        form_layout = QFormLayout()
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("Enter category name")
        form_layout.addRow("Category Name:", self.category_name_input)

        self.add_category_button = QPushButton("Add Category")
        self.add_category_button.clicked.connect(self.add_category)
        layout.addLayout(form_layout)
        layout.addWidget(self.add_category_button)

        # Categories Table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)  # Name and Actions
        self.categories_table.setHorizontalHeaderLabels(["Category Name", "Actions"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.categories_table.verticalHeader().setVisible(False)
        layout.addWidget(self.categories_table)

        # Load Categories Button
        self.load_categories_button = QPushButton("Refresh Categories")
        self.load_categories_button.clicked.connect(self.load_categories_table)
        layout.addWidget(self.load_categories_button)

        self.categories_tab.setLayout(layout)
        self.load_categories_table()
        
    def load_categories(self):
        """Loads drug categories into the dropdown."""
        api_url = os.getenv("PHARMACY_CATEGORIES_URL")
        categories = fetch_data(self, api_url, self.token)
        if categories:
            self.category_dropdown.clear()
            for category in categories:
                self.category_dropdown.addItem(category["name"], category["id"])

    def load_categories_table(self):
        """Loads drug categories into the categories table."""
        api_url = os.getenv("PHARMACY_CATEGORIES_URL")
        categories = fetch_data(self, api_url, self.token)
        if not categories:
            QMessageBox.information(self, "No Categories", "Please add categories")
            return

        self.categories_table.setRowCount(len(categories))
        for row, category in enumerate(categories):
            self.categories_table.setItem(row, 0, QTableWidgetItem(category["name"]))

            # Delete Button
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: #dc3545; color: white; padding: 5px;")
            delete_button.clicked.connect(lambda _, idx=category["id"]: self.delete_category(idx))
            self.categories_table.setCellWidget(row, 1, delete_button)

    def add_category(self):
        """Adds a new drug category."""
        category_name = self.category_name_input.text().strip()
        if not category_name:
            QMessageBox.warning(self, "Input Error", "Category name is required.")
            return

        api_url = os.getenv("PHARMACY_CATEGORIES_URL")
        data = {"name": category_name}
        response = post_data(self, api_url, data, self.token)

        if response:
            QMessageBox.information(self, "Success", "Category added successfully!")
            self.load_categories()  
            self.load_categories_table()  
            self.category_name_input.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to add category.")

    def delete_category(self, category_id):
        """Deletes a drug category."""
        confirm = QMessageBox.question(
            self, "Confirm Deletion", "Are you sure you want to delete this category?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.No:
            return

        api_url = os.getenv("PHARMACY_CATEGORIES_URL")
        delete_url = f"{api_url}{category_id}"
        response = delete_data(self, delete_url, self.token)

        if response:
            QMessageBox.information(self, "Success", "Category deleted successfully!")
            self.load_categories()  
            self.load_categories_table()  
        else:
            QMessageBox.critical(self, "Error", "Failed to delete category.")




    
    