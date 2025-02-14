from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QStackedWidget
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import os
import requests

class DashboardScreen(QWidget):
    def __init__(self, auth_handler):
        super().__init__()
        self.auth_handler = auth_handler
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QHBoxLayout()
        
        # Sidebar navigation
        self.sidebar = QListWidget()
        self.sidebar.addItem("Home")
        self.sidebar.addItem("Patients")
        self.sidebar.addItem("Doctors")
        self.sidebar.addItem("Pharmacy")
        self.sidebar.addItem("Laboratory")
        self.sidebar.addItem("Radiology")
        self.sidebar.addItem("ICU")
        self.sidebar.addItem("Logout")
        self.sidebar.setFixedWidth(200)
        self.sidebar.itemClicked.connect(self.handle_navigation)
        
        # Main content area
        self.main_content = QStackedWidget()
        
        self.home_page = QLabel("Welcome to the Hospital Management System")
        self.home_page.setFont(QFont("Arial", 14, QFont.Bold))
        self.home_page.setAlignment(Qt.AlignCenter)
        self.main_content.addWidget(self.home_page)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.main_content)
        
        self.setLayout(main_layout)
        
        self.check_authentication()
    
    def check_authentication(self):
        if not self.auth_handler.is_authenticated():
            self.close()
    
    def handle_navigation(self, item):
        if item.text() == "Logout":
            self.auth_handler.logout()
            self.close()
        else:
            self.main_content.setCurrentIndex(self.sidebar.row(item))
