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
            ("Patients", 0, ["admin", "nurse"]),  # Visible only to admin and nurses
            ("Doctors", 1, ["admin"]),
            ("Pharmacy", 2, ["admin", "pharmacist"]),
            ("Lab", 3, ["admin", "lab_technician"]),
            ("Radiology", 4, ["admin", "radiologist"]),
            ("ICU", 5, ["admin", "icu_staff"]),
            ("Appointments", 6, ["admin", "nurse", "doctor"]),
            ("Medical Records", 7, ["admin", "doctor", "nurse"]),
            ("Prescriptions", 8, ["admin", "doctor", "pharmacist"]),
            ("Billing", 9, ["admin", "billing_staff"]),
            ("Settings", 10, ["admin"]),
            ("User Management", 11, ["admin"]),
        ]

        # Create buttons dynamically based on role
        self.buttons = []
        for text, index, allowed_roles in menu_items:
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
                button.clicked.connect(lambda checked, i=index: self.parent.switch_module(i))
                layout.addWidget(button)
                self.buttons.append(button)

        self.setLayout(layout)
