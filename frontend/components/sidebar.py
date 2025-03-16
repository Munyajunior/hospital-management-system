from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, parent, role):
        super().__init__()
        self.parent = parent
        self.role = role  # Load user role
        self.init_ui()

    def init_ui(self):
        """Initialize the sidebar with navigation buttons based on user role."""
        self.setFixedWidth(220)  # Slightly wider for better aesthetics
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Define menu items with required roles
        menu_items = [
            ("Dashboard", "dashboard", ["admin", "nurse", "doctor", "pharmacist", "lab_technician", "radiologist", "icu_staff", "billing_staff"]),
            ("Patients", "patients", ["admin", "nurse"]),
            ("My Patients", "doctors", ["admin","doctor", "nurse", "receptionist"]),
            ("Admissions", "admission", ["admin","doctor", "nurse"]),
            ("Pharmacy", "pharmacy", ["pharmacist"]),
            ("Lab Test Request", "lab", ["doctor"]),
            ("Laboratory", "laboratory", ["lab_technician"]),
            ("Radiology", "radiology", ["radiologist"]),
            ("Radiography Request", "radiography_request", ["doctor"]),
            ("ICU", "icu", ["admin", "icu_staff"]),
            ("Appointments", "appointments", ["nurse", "doctor"]),
            ("Medical Records", "medical_records", ["admin", "doctor", "nurse"]),
            ("Prescriptions", "prescriptions", ["nurse", "doctor"]),
            ("Billing", "billing", ["admin", "billing_staff"]),
            ("Profile", "profile", ["admin", "nurse", "doctor", "pharmacist", "lab_technician", "radiologist", "icu_staff", "billing_staff"]),
            ("Settings", "settings", ["admin"]),
            ("User Management", "user_management", ["admin"]),
        ]

        # Create buttons dynamically based on role
        self.buttons = []
        for text, module, allowed_roles in menu_items:
            if self.role in allowed_roles:  # Check role permissions
                button = QPushButton(text)
                button.setFixedHeight(40)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2C3E50; 
                        color: white; 
                        font-size: 14px; 
                        border: none; 
                        padding: 10px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #34495E;
                    }
                    QPushButton:pressed {
                        background-color: #1A252F;
                    }
                """)
                # Fix: Correctly capture the module string
                button.clicked.connect(lambda checked, mod=module: self.parent.switch_module(mod))
                layout.addWidget(button)
                self.buttons.append(button)

        self.setLayout(layout)
