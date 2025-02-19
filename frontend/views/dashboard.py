from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from components.sidebar import Sidebar
from views.patient import PatientManagement
from views.doctor import DoctorManagement
from views.pharmacy import PharmacyManagement
from views.lab import LabManagement
from frontend.views.scans import RadiologyManagement
from views.icu import ICUManagement

class Dashboard(QWidget):
    def __init__(self, role):
        super().__init__()
        self.role = role
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Hospital Management System - Dashboard")
        self.setGeometry(100, 100, 1000, 600)

        main_layout = QHBoxLayout()

        # Sidebar Navigation
        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)

        # Main content area
        self.main_content = QStackedWidget()
        main_layout.addWidget(self.main_content)

        # Add different modules to the main content
        self.patient_management = PatientManagement()
        self.doctor_management = DoctorManagement()
        self.pharmacy_management = PharmacyManagement()
        self.lab_management = LabManagement()
        self.radiology_management = RadiologyManagement()
        self.icu_management = ICUManagement()

        self.main_content.addWidget(self.patient_management)
        self.main_content.addWidget(self.doctor_management)
        self.main_content.addWidget(self.pharmacy_management)
        self.main_content.addWidget(self.lab_management)
        self.main_content.addWidget(self.radiology_management)
        self.main_content.addWidget(self.icu_management)

        self.setLayout(main_layout)

    def switch_module(self, index):
        self.main_content.setCurrentIndex(index)
