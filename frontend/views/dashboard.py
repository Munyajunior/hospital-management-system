from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame, QApplication, QSizePolicy
)
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QTimer
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis
from components.sidebar import Sidebar
from utils.api_utils import fetch_data
from views.patients import PatientManagement
from views.doctors import DoctorManagement
from views.appointments import ManageAppointments
from views.medical_records import MedicalRecords
from views.prescriptions import Prescriptions
from views.pharmacy import Pharmacy
from views.scans import Scans
from views.radiology_management import RadiologyManagement
from views.lab_test import LabTests
from views.lab_test_management import LabTestManagement
from views.user_management import UserManagement
from views.billing import Billing
from views.profile import ProfileWindow
from views.admission import AdmissionManagement
import os
import sys


class Dashboard(QWidget):
    def __init__(self, role, user_id, auth_token):
        super().__init__()
        self.role = role
        self.user_id = user_id
        self.auth_token = auth_token
        self.init_ui()
        self.init_data_fetching()

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Hospital Management System - Dashboard")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(800, 600)  # Set a reasonable minimum size
        self.setStyleSheet("""
            QWidget { background: #f5f7fa; font-family: 'Arial', sans-serif; }
            QLabel { font-size: 16px; color: #2c3e50; }
            QPushButton { background-color: #3498db; color: white; border: none; padding: 10px; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1c5980; }
            QFrame { background: white; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0; }
        """)

        # Main Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Sidebar
        self.sidebar = Sidebar(self, self.role)
        main_layout.addWidget(self.sidebar)

        # Main Content Area
        self.main_content = QStackedWidget()
        self.main_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.main_content)

        # Dashboard View
        self.dashboard_view = QWidget()
        self.init_dashboard_view()
        self.main_content.addWidget(self.dashboard_view)

        # Dictionary to store dynamically loaded views
        self.views = {}

        self.setLayout(main_layout)

    def init_dashboard_view(self):
        """Initialize the dashboard view with metrics and charts."""
        layout = QVBoxLayout(self.dashboard_view)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel("🏥 Hospital Management Dashboard")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(header)

        # Sign Out Button
        self.sign_out_button = QPushButton("Logout")
        self.sign_out_button.setStyleSheet("""
            background-color: #ff4c4c;
            color: white;
            font-size: 14px;
            padding: 8px 20px;
            border-radius: 5px;
            font-weight: bold;
        """)
        self.sign_out_button.clicked.connect(self.logout_user)
        header_layout.addWidget(self.sign_out_button)
        layout.addLayout(header_layout)

        # Metrics Section
        self.metric_labels = {}  # Stores QLabel widgets
        self.metric_api_keys = {}  # Maps metric titles to API keys
        metrics_layout = QHBoxLayout()
        # Define metrics for each role
        self.role_metrics = {
            "admin": [
                {"title": "Total Patients", "value": "0", "icon": "assets/icons/patient.png", "api_key": "total_patients"},
                {"title": "Total Lab Tests", "value": "0", "icon": "assets/icons/lab.png", "api_key": "total_lab_tests"},
                {"title": "Total Scans", "value": "0", "icon": "assets/icons/scan.png", "api_key": "total_scans"},
                {"title": "Total Prescriptions", "value": "0", "icon": "assets/icons/prescription.png", "api_key": "total_prescriptions"},
                {"title": "Appointments", "value": "0", "icon": "assets/icons/date.png", "api_key": "total_appointments"},
                {"title": "Billing Transactions", "value": "0", "icon": "assets/icons/payment.png", "api_key": "total_billing_transactions"},
                {"title": "Predicted Admissions", "value": "0", "icon": "assets/icons/admissions.png", "api_key": "predicted_admissions"},
            ],
            "doctor": [
                {"title": "My Patients", "value": "0", "icon": "assets/icons/patient.png", "api_key": "my_patients"},
                {"title": "My Appointments", "value": "0", "icon": "assets/icons/date.png", "api_key": "my_appointments"},
                {"title": "No-Show Rate", "value": "0%", "icon": "assets/icons/no_show.png", "api_key": "no_show_rate"},
                {"title": "Predicted Admissions", "value": "0", "icon": "assets/icons/admissions.png", "api_key": "predicted_admissions"},
            ],
            "nurse":[
                {"title": "Total Admissions", "value": "0", "icon": "assets/icons/admission.png", "api_key": "total_admissions"},
                {"title": "Total Admissions", "value": "0", "icon": "assets/icons/date.png", "api_key":"total_appointments"},
                {"title": "Predicted Admissions", "value": "0", "icon": "assets/icons/admissions.png", "api_key": "predicted_admissions"},
            ],
            "pharmacist": [
                {"title": "Total Prescriptions", "value": "0", "icon": "assets/icons/prescription.png", "api_key": "total_prescriptions"},
                {"title": "Pending Prescriptions", "value": "0", "icon": "assets/icons/prescription.png", "api_key": "pending_prescriptions"},
            ],
            "lab_technician":[
                {"title": "Total Lab Tests", "value": "0", "icon": "assets/icons/lab.png", "api_key": "total_lab_tests"},
                {"title": "Pending Lab Tests", "value": "0", "icon": "assets/icons/result.png", "api_key": "pending_lab_tests"},
                {"title": "Lab Tests In Progress", "value": "0", "icon": "assets/icons/result.png", "api_key": "lab_tests_in_progress"},
            ],
            "radiologist": [
                {"title": "Total Scans", "value": "0", "icon": "assets/icons/scan.png", "api_key": "total_scans"},
                {"title": "Pending Scans", "value": "0", "icon": "assets/icons/result.png", "api_key": "pending_scans"},
                {"title": "Scans In Progress", "value": "0", "icon": "assets/icons/result.png", "api_key": "scans_in_progress"},
            ]
        }
                             

         # Add metrics based on the user's role
        for metric in self.role_metrics.get(self.role, []):
            self.add_metric(metrics_layout, metric["title"], metric["value"], metric["icon"])
            self.metric_api_keys[metric["title"]] = metric["api_key"]  # Store API key
        
        layout.addLayout(metrics_layout)
        
        # Charts Section
        charts_layout = QHBoxLayout()
        self.pie_chart_series = QPieSeries()
        self.pie_chart_view = self.create_pie_chart()
        charts_layout.addWidget(self.pie_chart_view)

        self.bar_chart_set0 = QBarSet("Completed")
        self.bar_chart_set1 = QBarSet("Pending")
        self.bar_chart_view = self.create_bar_chart()
        charts_layout.addWidget(self.bar_chart_view)
        layout.addLayout(charts_layout)

    def add_metric(self, layout, title, value, icon_path):
        """Add a metric box to the dashboard."""
        metric_box = QFrame()
        metric_box.setStyleSheet("""
            background: white;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #e0e0e0;
        """)
        metric_box.setFixedWidth(200)

        vbox = QVBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #333333; padding: 5px;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: #007BFF; font-size: 16px;")
        self.metric_labels[title] = value_label

        vbox.addWidget(icon_label)
        vbox.addWidget(title_label)
        vbox.addWidget(value_label)
        metric_box.setLayout(vbox)
        layout.addWidget(metric_box)
    def create_pie_chart(self):
        """Create a pie chart for patient distribution."""
        series = self.pie_chart_series
        series.append("Outpatients", 0).setBrush(QColor("#3498db"))
        series.append("Inpatients", 0).setBrush(QColor("#2ecc71"))
        series.append("ICU", 0).setBrush(QColor("#e74c3c"))
        series.append("Emergency", 0).setBrush(QColor("#f1c40f"))

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Patient Distribution")
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(250)
        return chart_view

    def create_bar_chart(self):
        """Create a bar chart for daily appointments."""
        set0 = self.bar_chart_set0
        set1 = self.bar_chart_set1
        set0.append([0])
        set1.append([0])

        series = QBarSeries()
        series.append(set0)
        series.append(set1)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Daily Appointments")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        categories = ["Today"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axisX, series)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(250)
        return chart_view

    def init_data_fetching(self):
        """Initialize data fetching and periodic updates."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard_data)
        self.timer.start(5000000)  # Refresh data every 5 seconds
        self.update_dashboard_data()  # Initial data fetch

    def update_dashboard_data(self):
        """Fetch and update dashboard data from the backend."""
        metrics = fetch_data(self, f"{os.getenv('API_BASE_URL')}/dashboard/metrics", self.auth_token)
        if metrics:
            self.update_metrics(metrics)
            self.update_doctor_metrics()
            self.update_pie_chart(metrics["patient_distribution"])
            #self.update_bar_chart(metrics["appointments_data"])
        self.update_ai_metric()
            
    def update_metrics(self, metrics):
        """Update the dashboard metrics dynamically."""
        for title, value_label in self.metric_labels.items():
            # Find the corresponding API key for the metric title
            api_key = self.metric_api_keys.get(title)
            if api_key and api_key in metrics:
                value = metrics[api_key]
                if title == "No-Show Rate":
                    value = f"{value * 100:.2f}%"  # Format as percentage
                value_label.setText(str(value))

    def update_doctor_metrics(self):
        """Fetch and update doctor-specific metrics."""
        metrics = fetch_data(self, f"{os.getenv('API_BASE_URL')}/dashboard/metrics/doctor/{self.user_id}", self.auth_token)
        if metrics:
            for title, value_label in self.metric_labels.items():
                api_key = self.metric_api_keys.get(title)
                if api_key and api_key in metrics:
                    value = metrics[api_key]
                    value_label.setText(str(value))

    def update_ai_metric(self):
        """Fetch and update AI-driven metrics."""
        pa_ai = fetch_data(self, f"{os.getenv('AI_BASE_URL')}/predict-admissions", self.auth_token)
        if pa_ai:
            self.update_ai_admissions_prediction_metrics(pa_ai)
        #no_sh_ai = fetch_data(self, f"{os.getenv('AI_BASE_URL')}/predict-no-show", self.auth_token)
    

    def update_pie_chart(self, patient_distribution):
        """Update the pie chart with patient distribution data."""
        self.pie_chart_series.clear()
        self.pie_chart_series.append("Outpatients", patient_distribution["outpatients"])
        self.pie_chart_series.append("Inpatients", patient_distribution["inpatients"])
        self.pie_chart_series.append("ICU", patient_distribution["icu"])
        self.pie_chart_series.append("Emergency", patient_distribution["emergency"])
        
    def update_bar_chart(self, appointments_data):
        """Update the bar chart with appointments data."""
        self.bar_chart_set0.replace([appointments_data["completed"]])
        self.bar_chart_set1.replace([appointments_data["pending"]])
    
    def update_ai_admissions_prediction_metrics(self, metrics):
        """Update AI-driven metrics."""
        self.metric_labels["Predicted Admissions"].setText(str(metrics["predicted_admissions"][0]))
        
    def update_ai_no_show_rate(self, metrics):
        """Update AI-driven metrics."""
        self.metric_labels["No-Show Rate"].setText(f"{metrics['no_show_rate'] * 100:.2f}%")
   
    def logout_user(self):
        """Log out the user and restart the application."""
        print("Logging out user...")
        self.auth_token = None
        self.user_id = None
        python = sys.executable
        os.execl(python, python, "main.py")
        
    def switch_module(self, module):
        """Switches between different modules and hides the dashboard when another module is selected."""
        if module == "dashboard":
            self.main_content.setCurrentWidget(self.dashboard_view)
        else:
            if module not in self.views:
                if module == "patients":
                    self.views[module] = PatientManagement(self.role, self.user_id, self.auth_token)
                elif module == "doctors":
                    self.views[module] = DoctorManagement(self.role, self.user_id, self.auth_token)
                elif module == "appointments":
                    self.views[module] = ManageAppointments(self.role, self.user_id, self.auth_token)
                elif module == "medical_records":
                    self.views[module] = MedicalRecords(self.role, self.user_id, self.auth_token)
                elif module == "prescriptions":
                    self.views[module] = Prescriptions(self.role, self.user_id, self.auth_token)
                elif module == "pharmacy":
                    self.views[module] = Pharmacy(self.role, self.user_id, self.auth_token)
                elif module == "radiography_request":
                    self.views[module] = Scans(self.role, self.user_id, self.auth_token)
                elif module == "radiology":
                    self.views[module] = RadiologyManagement(self.role, self.user_id, self.auth_token)
                elif module == "lab":
                    self.views[module] = LabTests(self.role, self.user_id, self.auth_token)
                elif module == "laboratory":
                    self.views[module] = LabTestManagement(self.role, self.user_id, self.auth_token)
                elif module == "user_management":
                    self.views[module] = UserManagement(self.role, self.user_id, self.auth_token)
                elif module == "billing":
                    self.views[module] = Billing(self.role, self.user_id, self.auth_token)
                elif module == "profile":
                    self.views[module] = ProfileWindow(self.user_id, self.auth_token)
                elif module == "admission":
                    self.views[module] = AdmissionManagement(self.role, self.user_id, self.auth_token)
                # Add more views here...

                self.main_content.addWidget(self.views[module])

            self.main_content.setCurrentWidget(self.views[module])  # Show selected module

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Check if the current widget is the dashboard_view
        if self.main_content.currentWidget() == self.dashboard_view:
            # Resize charts and other components dynamically
            self.pie_chart_view.setFixedHeight(self.height() * 0.3)
            self.bar_chart_view.setFixedHeight(self.height() * 0.3)