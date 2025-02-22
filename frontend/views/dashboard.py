from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from components.sidebar import Sidebar
from views.patients import PatientManagement
from views.doctors import DoctorManagement
from views.pharmacy import Pharmacy
from views.lab_test_management import LabTestManagement
from views.radiology_management import RadiologyManagement
from views.icu_management import ICUManagement
from views.appointments import Appointments
from views.medical_records import MedicalRecords
from views.prescriptions import Prescriptions
from views.billing import Billing
from views.settings import Settings
from views.user_management import UserManagement

class Dashboard(QWidget):
    def __init__(self, role, user_id, auth_token):
        super().__init__()
        self.role = role
        self.user_id = user_id
        self.auth_token = auth_token
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Hospital Management System - Dashboard")
        self.setGeometry(100, 100, 1200, 800)

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
        #self.pharmacy_management = Pharmacy(self.role, self.user_id, self.auth_token)
        # self.lab_management = LabTestManagement(self.role, self.user_id, self.auth_token)
        # self.radiology_management = RadiologyManagement(self.role, self.user_id, self.auth_token)
        # self.icu_management = ICUManagement(self.role, self.user_id, self.auth_token)
        # self.appointments = Appointments(self.role, self.user_id)
        # self.medical_records = MedicalRecords(self.role, self.user_id)
        # self.prescriptions = Prescriptions(self.role, self.user_id)
        # self.billing = Billing(self.auth_token, self.role)
        # self.settings = Settings(self.auth_token, self.role)
        # self.user_management = UserManagement(self.auth_token, self.role)

        self.main_content.addWidget(self.patient_management)
        self.main_content.addWidget(self.doctor_management)
        # self.main_content.addWidget(self.pharmacy_management)
        # self.main_content.addWidget(self.lab_management)
        # self.main_content.addWidget(self.radiology_management)
        # self.main_content.addWidget(self.icu_management)
        # self.main_content.addWidget(self.appointments)
        # self.main_content.addWidget(self.medical_records)
        # self.main_content.addWidget(self.prescriptions)
        # self.main_content.addWidget(self.billing)
        # self.main_content.addWidget(self.settings)
        # self.main_content.addWidget(self.user_management)

        self.setLayout(main_layout)

    def switch_module(self, index):
        self.main_content.setCurrentIndex(index)