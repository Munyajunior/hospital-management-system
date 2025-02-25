from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame
from PySide6.QtGui import QFont, QIcon, QPainter, QPen
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice, QBarSet, QBarSeries, QBarCategoryAxis
from components.sidebar import Sidebar
from views.patients import PatientManagement
from views.doctors import DoctorManagement
import os
import sys
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
        self.setStyleSheet("background-color: #F5F5F5;")  # Light background

        main_layout = QHBoxLayout()
        
        # Sidebar Navigation
        self.sidebar = Sidebar(self, self.role)
        main_layout.addWidget(self.sidebar)

        # Main content area
        content_layout = QVBoxLayout()

        # Header Section with Sign Out Button
        header_layout = QHBoxLayout()

        # Header Section
        header = QLabel("Hospital Management System Dashboard")
        #header.setIcon(QIcon("assets/icons/hospital.png"))
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #333; padding: 10px; background-color: #EAEAEA; border-radius: 5px;")

        header_layout.addWidget(header)
        
         # Sign Out Button
        self.sign_out_button = QPushButton("Sign Out")
        self.sign_out_button.setStyleSheet("""
            background-color: #FF4C4C; 
            color: white; 
            font-size: 14px; 
            padding: 5px 15px; 
            border-radius: 5px;
        """)
        self.sign_out_button.clicked.connect(self.logout_user)
        header_layout.addWidget(self.sign_out_button)
        content_layout.addLayout(header_layout)

        # Metrics Section
        metrics_layout = QHBoxLayout()
        self.add_metric(metrics_layout, "Total Patients", "1200")
        self.add_metric(metrics_layout, "Appointments Today", "45")
        self.add_metric(metrics_layout, "Pending Lab Tests", "30")
        self.add_metric(metrics_layout, "Billing Transactions", "75")
        content_layout.addLayout(metrics_layout)

        # Charts Section
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.create_pie_chart())
        charts_layout.addWidget(self.create_bar_chart())
        content_layout.addLayout(charts_layout)

        # Main Stacked Content Area (Hidden Modules)
        self.main_content = QStackedWidget()
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
        
        if self.role == "admin" or self.role == "nurse":
            self.main_content.addWidget(self.patient_management)
        if self.role == "doctor" or self.role == "admin":
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

        content_layout.addWidget(self.main_content)

        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def add_metric(self, layout, title, value):
        """Creates a simple metric display with a title and value."""
        metric_box = QFrame()
        metric_box.setFrameShape(QFrame.Box)
        metric_box.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px;")
        metric_box.setFixedWidth(200)

        vbox = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: #007BFF;")  # Blue color for emphasis

        vbox.addWidget(title_label)
        vbox.addWidget(value_label)
        metric_box.setLayout(vbox)
        layout.addWidget(metric_box)
    
    def logout_user(self):
        """Logs out the user and restarts the application to show the login screen."""
        print("Logging out user...")

        # Clear authentication details
        self.auth_token = None
        self.user_id = None

        # Restart the application
        python = sys.executable
        os.execl(python, python, "main.py")  # Restart main.py

    def create_pie_chart(self):
        """Creates a pie chart for patient distribution by department."""
        series = QPieSeries()
        series.append("Outpatients", 500)
        series.append("Inpatients", 350)
        series.append("ICU", 100)
        series.append("Emergency", 250)

        for slice in series.slices():
            slice.setLabel(f"{slice.label()} - {slice.value()}")

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Patient Distribution")
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(250)
        return chart_view

    def create_bar_chart(self):
        """Creates a bar chart for daily appointments."""
        set0 = QBarSet("Completed")
        set1 = QBarSet("Pending")
        set0.append([20, 25, 30, 22, 28])
        set1.append([10, 15, 10, 12, 7])

        series = QBarSeries()
        series.append(set0)
        series.append(set1)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Daily Appointments")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axisX, series)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(250)
        return chart_view

    def switch_module(self, index):
        """Switches between different modules in the dashboard."""
        self.main_content.setCurrentIndex(index)
