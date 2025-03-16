import os
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QFrame, QSizePolicy, QComboBox, QTextEdit, QMessageBox,
    QCalendarWidget, QDialog
)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QFont
from utils.api_utils import fetch_data, post_data, update_data, delete_data

class ManageAppointments(QWidget):
    def __init__(self, user_role, user_id, token):
        super().__init__()
        self.user_role = user_role
        self.doctor_id = user_id
        self.token = token
        self.dark_mode = True  # Default to dark mode

        self.setWindowTitle("Appointments Dashboard")
        self.setGeometry(200, 100, 800, 600)
        self.init_ui()
        self.load_appointments()

    def init_ui(self):
        """Initialize UI components"""
        self.layout = QHBoxLayout(self)

        # Sidebar Menu
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("""
            QFrame { background-color: #282a36; border-right: 2px solid #44475a; }
        """)

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(15)

        self.title_label = QLabel("📅 Appointments")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.title_label)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("background: #6272a4; padding: 8px; border-radius: 5px;")
        self.refresh_btn.clicked.connect(self.load_appointments)
        self.sidebar_layout.addWidget(self.refresh_btn)

        self.toggle_theme_btn = QPushButton("🌙 Light Mode")
        self.toggle_theme_btn.setStyleSheet("background: #50fa7b; padding: 8px; border-radius: 5px;")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        self.sidebar_layout.addWidget(self.toggle_theme_btn)

        self.layout.addWidget(self.sidebar)

        # Main Content Area
        self.main_frame = QFrame()
        self.main_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout(self.main_frame)

        self.header_label = QLabel("📋 Scheduled Appointments")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header_label)

        self.appointment_list = QListWidget()
        self.appointment_list.setStyleSheet("""
            QListWidget { background-color: #44475a; border: none; font-size: 14px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #6272a4; }
            QListWidget::item:selected { background-color: #50fa7b; color: black; }
        """)
        self.main_layout.addWidget(self.appointment_list)

        # Appointment Form Section
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("background: #282a36; padding: 15px; border-radius: 10px;")
        self.form_layout = QVBoxLayout(self.form_frame)

        self.form_title = QLabel("➕ Schedule Appointment")
        self.form_layout.addWidget(self.form_title)

        self.patient_dropdown = QComboBox()
        self.patient_dropdown.setPlaceholderText("Select a Patient")
        self.load_patients()
        self.patient_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px;")
        self.form_layout.addWidget(self.patient_dropdown)
        
        if self.user_role == "nurse":
            self.doctor_dropdown = QComboBox()
            self.doctor_dropdown.setPlaceholderText("Select his/her Doctor")
            self.load_doctors()
            self.doctor_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px;")
            self.form_layout.addWidget(self.doctor_dropdown) 

        self.calendar_widget_label = QLabel("Select Date")
        self.calendar_widget_label.setStyleSheet("background: #6272a4; padding: 8px; border-radius: 5px;")
        self.form_layout.addWidget(self.calendar_widget_label)
        
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px;")
        self.form_layout.addWidget(self.calendar_widget)

        # Create Time Dropdown for Hour Selection
        self.hour_dropdown = QComboBox()
        self.hour_dropdown.setPlaceholderText("Select an Hour")
        self.hour_dropdown.addItems([f"{h:02d}" for h in range(24)])  # 00 - 23 hours
        self.hour_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px;")
        self.form_layout.addWidget(self.hour_dropdown)
        
        # Create Time Dropdown for Minute Selection
        self.minute_dropdown = QComboBox()
        self.minute_dropdown.setPlaceholderText("Select a minute")
        self.minute_dropdown.addItems([f"{m:02d}" for m in range(0, 60, 15)])  # 00, 15, 30, 45
        self.minute_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px;")
        self.form_layout.addWidget(self.minute_dropdown)

        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Enter reason for appointment...")
        self.reason_input.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px;")
        self.form_layout.addWidget(self.reason_input)

        self.schedule_button = QPushButton("📌 Schedule")
        self.schedule_button.setStyleSheet("background: #50fa7b; padding: 8px; border-radius: 5px;")
        self.schedule_button.clicked.connect(self.schedule_appointment)
        self.form_layout.addWidget(self.schedule_button)

        self.main_layout.addWidget(self.form_frame)
        self.layout.addWidget(self.main_frame)

        self.setLayout(self.layout)

    def load_patients(self):
        if self.user_role == "doctor":
            """Load patients into dropdown."""
            api_url = f"{os.getenv('ASSIGNED_PATIENTS_URL')}/{self.doctor_id}/patients"
            patients = fetch_data(self, api_url, self.token)
            self.patient_dropdown.clear()

            if not patients:
                return

            for patient in patients:
                self.patient_dropdown.addItem(f"{patient['full_name']} (ID: {patient['id']})", patient["id"])
        else:
            api_url = os.getenv('PATIENT_LIST_URL')
            patients = fetch_data(self, api_url, self.token)
            self.patient_dropdown.clear()

            if not patients:
                return

            for patient in patients:
                self.patient_dropdown.addItem(f"{patient['full_name']} (ID: {patient['id']})", patient["id"])
    def load_doctors(self):
        api_url = os.getenv('DOCTOR_LIST_URL')
        doctors = fetch_data(self, api_url, self.token)
        self.doctor_dropdown.clear()

        if not doctors:
            return

        for doctor in doctors:
            self.doctor_dropdown.addItem(f"{doctor['full_name']} (ID: {doctor['id']})", doctor["id"])

    def load_appointments(self):
        if self.user_role == "doctor":
            """Load and display appointments in list format."""
            api_url = f"{os.getenv('APPOINTMENTS_URL')}/doctor/{self.doctor_id}/"
            appointments = fetch_data(self, api_url, self.token)

            self.appointment_list.clear()

            # Create a "header" item (not selectable)
            header_item = QListWidgetItem("🆔 ID       Patient Name            Date & Time                 Status")
            header_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            header_item.setFont(QFont("Arial", 12, QFont.Bold))  # Bold font for header
            self.appointment_list.addItem(header_item)

            if appointments:
                for appointment in appointments:
                    item = QListWidgetItem(
                        f"{appointment['id']:<14}   {appointment['patient_name']:<25}   {appointment['datetime']:<25}   {appointment['status']}"
                    )
                    item.setData(Qt.UserRole, appointment)
                    item.setSizeHint(QSize(0, 50))
                    self.appointment_list.addItem(item)
            else:
                # Show empty state message
                no_data_item = QListWidgetItem("No appointments scheduled.")
                no_data_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
                self.appointment_list.addItem(no_data_item)
        else:
            """Load and display appointments in list format."""
        api_url = f"{os.getenv('APPOINTMENTS_URL')}/"
        appointments = fetch_data(self, api_url, self.token)

        self.appointment_list.clear()

        # Create a "header" item (not selectable)
        header_item = QListWidgetItem("🆔 ID       Patient Name            Date & Time                 Status                 Doctor in Charge")
        header_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
        header_item.setFont(QFont("Arial", 12, QFont.Bold))  # Bold font for header
        self.appointment_list.addItem(header_item)

        if appointments:
            for appointment in appointments:
                item = QListWidgetItem(
                    f"{appointment['id']:<14}   {appointment['patient_name']:<25}   {appointment['datetime']:<25}   {appointment['status']:<25} {appointment['doctor_id']:}"
                )
                item.setData(Qt.UserRole, appointment)
                item.setSizeHint(QSize(0, 50))
                self.appointment_list.addItem(item)
        else:
            # Show empty state message
            no_data_item = QListWidgetItem("No appointments scheduled.")
            no_data_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
            self.appointment_list.addItem(no_data_item)

        self.appointment_list.itemClicked.connect(self.show_appointment_details)



    def show_appointment_details(self, item):
        """Display appointment details with options to update, reschedule, or cancel."""
        appointment = item.data(Qt.UserRole)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Appointment Details")
        msg.setText(
            f"📌 Patient: {appointment['patient_name']}\n"
            f"🗓 Date/Time: {appointment['datetime']}\n"
            f"📄 Reason: {appointment['reason']}\n"
            f"📄 Status: {appointment['status']}\n\n"
            "Select an action below:"
        )
        
        update_btn = msg.addButton("📝 Completed", QMessageBox.ActionRole)
        reschedule_btn = msg.addButton("⏳ Reschedule", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("❌ Cancel", QMessageBox.ActionRole)
        delete_btn = msg.addButton("❌ Delete", QMessageBox.ActionRole)
        close_btn = msg.addButton(QMessageBox.Close)

        msg.exec_()

        if msg.clickedButton() == update_btn:
            self.update_appointment(appointment)
        elif msg.clickedButton() == reschedule_btn:
            self.reschedule_appointment(appointment)
        elif msg.clickedButton() == cancel_btn:
            self.cancel_appointment(appointment)
        elif msg.clickedButton() == delete_btn:
            self.delete_appointment(appointment)

    def schedule_appointment(self):
        """Schedule a new appointment."""
        patient_text = self.patient_dropdown.currentText()
        match = re.match(r"(.+) \(ID: (\d+)\)", patient_text)

        if match:
            patient_name = match.group(1)  # Extract full name
            patient_id = int(match.group(2))  # Extract ID as integer
        else:
            QMessageBox.warning(self, "Error", "Invalid patient selection. Please select a valid patient.")
            return

        # Get Selected Date from Calendar
        selected_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")

        # Get Selected Time from Dropdowns
        selected_hour = self.hour_dropdown.currentText()
        selected_minute = self.minute_dropdown.currentText()

        # Combine Date and Time
        datetime_str = f"{selected_date} {selected_hour}:{selected_minute}:00"

        reason = self.reason_input.toPlainText().strip()

        if not reason:
            QMessageBox.warning(self, "Error", "Enter a reason!")
            return
        
        if self.user_role == "doctor":
            api_url = f"{os.getenv('APPOINTMENTS_URL')}/"
            data = {
                "doctor_id": self.doctor_id,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "datetime": datetime_str,
                "reason": reason
            }

            if post_data(self, api_url, data, self.token):
                QMessageBox.information(self, "Success", "Appointment scheduled!")
                self.load_appointments()
                self.reason_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to schedule appointment.")
        else:
            doctor_text = self.doctor_dropdown.currentText()
            match2 = re.match(r"(.+) \(ID: (\d+)\)", doctor_text)

            if match:
                doctor_name = match.group(1)  # Extract full name
                doctor_id = int(match.group(2))  # Extract ID as integer
            else:
                QMessageBox.warning(self, "Error", "Invalid Doctor selection. Please select a valid Doctor.")
                return
            
            api_url = f"{os.getenv('APPOINTMENTS_URL')}/"
            data = {
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "datetime": datetime_str,
                "reason": reason
            }

            if post_data(self, api_url, data, self.token):
                QMessageBox.information(self, "Success", "Appointment scheduled!")
                self.load_appointments()
                self.reason_input.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to schedule appointment.")

    def update_appointment(self, appointment):
       
        api_url = f"{os.getenv('APPOINTMENTS_URL')}/{appointment['id']}/update"
        data = {"status": "Completed"}
        
        if update_data(self, api_url, data, self.token):
            QMessageBox.information(self, "Updated", "Appointment updated successfully.")
            self.load_appointments()

    def cancel_appointment(self, appointment):
        """Cancel an appointment."""
        confirm = QMessageBox.question(self, "Cancel Appointment", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        
        api_url = f"{os.getenv('APPOINTMENTS_URL')}/{appointment['id']}/update"
        data ={
            "status": "Canceled"
        }
        if update_data(self, api_url ,data ,self.token):
            QMessageBox.information(self, "Cancelled", "Appointment cancelled.")
            self.load_appointments()
    
    def delete_appointment(self, appointment):
        """delete an appointment."""
        confirm = QMessageBox.question(self, "Delete Appointment", "Are you sure?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        
        api_url = f"{os.getenv('APPOINTMENTS_URL')}/{appointment['id']}"
        if delete_data(self, api_url, self.token):
            QMessageBox.information(self, "Cancelled", "Appointment cancelled.")
            self.load_appointments()

    def reschedule_appointment(self, appointment):
        """Reschedule an appointment using an easy-to-use date picker and time dropdown."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Reschedule Appointment")

        layout = QVBoxLayout()

        # Calendar widget for date selection
        calendar = QCalendarWidget()
        calendar.setMinimumDate(QDate.currentDate())  # Prevent selecting past dates
        layout.addWidget(calendar)

        # Time slot selection dropdown
        time_dropdown = QComboBox()
        time_slots = ["08:00 AM", "09:30 AM", "11:00 AM", "01:30 PM", "03:00 PM", "04:30 PM"]
        time_dropdown.addItems(time_slots)
        layout.addWidget(time_dropdown)

        # Confirm button
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(lambda: dialog.accept())
        layout.addWidget(confirm_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: dialog.reject())
        layout.addWidget(cancel_button)

        dialog.setLayout(layout)

        if dialog.exec():  # If user confirms
            selected_date = calendar.selectedDate().toString("yyyy-MM-dd")
            selected_time = time_dropdown.currentText()

            # Convert time slot to 24-hour format
            time_conversion = {
                "08:00 AM": "08:00:00",
                "09:30 AM": "09:30:00",
                "11:00 AM": "11:00:00",
                "01:30 PM": "13:30:00",
                "03:00 PM": "15:00:00",
                "04:30 PM": "16:30:00",
            }
            selected_time_24h = time_conversion[selected_time]

            new_datetime = f"{selected_date} {selected_time_24h}"

            api_url = f"{os.getenv('APPOINTMENTS_URL')}/{appointment['id']}/reschedule"
            data = {
                "datetime": new_datetime,
                "status": "Rescheduled" 
            }

            if update_data(self, api_url, data, self.token):
                QMessageBox.information(self, "Rescheduled", "Appointment rescheduled successfully.")
                self.load_appointments()
                
                
    def toggle_theme(self):
        """Toggle between dark and light mode."""
        if self.dark_mode:
            self.setStyleSheet("QWidget { background-color: white; color: black; }")
            self.toggle_theme_btn.setText("🌙 Dark Mode")
        else:
            self.setStyleSheet("QWidget { background-color: #1e1e2e; color: white; }")
            self.toggle_theme_btn.setText("☀️ Light Mode")

        self.dark_mode = not self.dark_mode

        
    # def get_text_input(self, title, label, default=""):
    #     """Helper function to get text input from user."""
    #     text, ok = QInputDialog.getText(self, title, label, text=default)
    #     return text, ok

    # def get_datetime_input(self, title, label):
    #     """Helper function to get a datetime input from user."""
    #     datetime_edit = QDateTimeEdit()
    #     datetime_edit.setCalendarPopup(True)
    #     datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
    #     ok = QMessageBox.question(self, title, label, QMessageBox.Ok | QMessageBox.Cancel)
    #     return datetime_edit.dateTime(), ok == QMessageBox.Ok

    
