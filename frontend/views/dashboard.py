from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QFrame
from PySide6.QtGui import QFont, QPixmap, QPainter
from PySide6.QtCore import Qt
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSet, QBarSeries, QBarCategoryAxis
from components.sidebar import Sidebar
from views.patients import PatientManagement
from views.doctors import DoctorManagement
from views.appointments import ManageAppointments
from views.medical_records import MedicalRecords
from views.prescriptions import Prescriptions
import os
import sys

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
        self.setStyleSheet("""
            background: qlineargradient(spread: pad, x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #D9E4F5, stop: 1 #FFFFFF);
            font-family: Arial;
        """)

        main_layout = QHBoxLayout()

        # Sidebar
        self.sidebar = Sidebar(self, self.role)
        main_layout.addWidget(self.sidebar)

        # Main content area
        self.main_content = QStackedWidget()
        
        # Dashboard View (Index 0)
        self.dashboard_view = QWidget()
        dashboard_layout = QVBoxLayout()

        # Header Section
        header_layout = QHBoxLayout()
        header = QLabel("🏥 Hospital Management Dashboard")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            background-color: #007BFF;
            color: white;
            padding: 8px 15px;
            border-radius: 6px;
        """)
        header_layout.addWidget(header)

        # Sign Out Button
        self.sign_out_button = QPushButton("Logout")
        self.sign_out_button.setStyleSheet("""
            background-color: #FF4C4C; 
            color: white; 
            font-size: 14px; 
            padding: 8px 20px; 
            border-radius: 5px;
            font-weight: bold;
        """)
        self.sign_out_button.clicked.connect(self.logout_user)
        header_layout.addWidget(self.sign_out_button)
        dashboard_layout.addLayout(header_layout)

        # Metrics Section
        metrics_layout = QHBoxLayout()
        self.add_metric(metrics_layout, "Total Patients", "1200", "assets/icons/patient.png")
        self.add_metric(metrics_layout, "Appointments", "45", "assets/icons/date.png")
        self.add_metric(metrics_layout, "Pending Lab Tests", "30", "assets/icons/result.png")
        self.add_metric(metrics_layout, "Billing Transactions", "75", "assets/icons/payment.png")
        dashboard_layout.addLayout(metrics_layout)

        # Charts Section
        charts_layout = QHBoxLayout()
        charts_layout.addWidget(self.create_pie_chart())
        charts_layout.addWidget(self.create_bar_chart())
        dashboard_layout.addLayout(charts_layout)

        self.dashboard_view.setLayout(dashboard_layout)
        self.main_content.addWidget(self.dashboard_view)  # Dashboard at index 0
        self.views = {"dashboard": self.dashboard_view}  # Add dashboard view to self.views

        # Dictionary to store dynamically loaded views
        self.views = {}

        main_layout.addWidget(self.main_content)
        self.setLayout(main_layout)

    def add_metric(self, layout, title, value, icon_path):
        """Creates a modern metric display with an icon, title, and value."""
        metric_box = QFrame()
        metric_box.setFrameShape(QFrame.Box)
        metric_box.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #E0E0E0;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
        """)
        metric_box.setFixedWidth(200)

        vbox = QVBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(40, 40, Qt.KeepAspectRatio))
        icon_label.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)  # Allow word wrapping
        title_label.setStyleSheet("color: #333333; padding: 5px;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: #007BFF; font-size: 16px;")

        vbox.addWidget(icon_label)
        vbox.addWidget(title_label)
        vbox.addWidget(value_label)
        metric_box.setLayout(vbox)
        layout.addWidget(metric_box)

    def logout_user(self):
        """Logs out the user and restarts the application to show the login screen."""
        print("Logging out user...")
        self.auth_token = None
        self.user_id = None
        python = sys.executable
        os.execl(python, python, "main.py")  # Restart main.py

    def create_pie_chart(self):
        """Creates a modern pie chart for patient distribution."""
        series = QPieSeries()
        series.append("Outpatients", 500).setBrush(Qt.GlobalColor.cyan)
        series.append("Inpatients", 350).setBrush(Qt.GlobalColor.green)
        series.append("ICU", 100).setBrush(Qt.GlobalColor.red)
        series.append("Emergency", 250).setBrush(Qt.GlobalColor.yellow)

        for slice in series.slices():
            slice.setLabel(f"{slice.label()} - {int(slice.value())}")

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Patient Distribution")
        chart.legend().setAlignment(Qt.AlignBottom)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(250)
        return chart_view

    def create_bar_chart(self):
        """Creates an animated bar chart for daily appointments."""
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

        categories = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axisX, series)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(250)
        return chart_view

    def switch_module(self, module):
        """Switches between different modules and hides the dashboard when another module is selected."""
        if module == "dashboard":
            # Ensure the dashboard view is in self.views
            if "dashboard" not in self.views:
                self.views["dashboard"] = self.dashboard_view
            self.main_content.setCurrentWidget(self.views["dashboard"])  # Switch to dashboard view
        else:
            # If module isn't in views, create and add it
            if module not in self.views:
                if module == "patients":
                    self.views[module] = PatientManagement()
                elif module == "doctors":
                    self.views[module] = DoctorManagement()
                elif module == "appointments":
                    self.views[module] = ManageAppointments(self.role, self.user_id, self.auth_token)
                elif module == "medical_records":
                    self.views[module] = MedicalRecords(self.role, self.user_id, self.auth_token)
                elif module == "prescriptions":
                    self.views[module] = Prescriptions(self.role, self.user_id, self.auth_token)
                # Add more views here...

                self.main_content.addWidget(self.views[module])

            self.main_content.setCurrentWidget(self.views[module])  # Show selected module
