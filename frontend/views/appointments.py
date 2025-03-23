import os
import re
import requests
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication,
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QHBoxLayout, QFrame, QSizePolicy, QComboBox, QTextEdit, QMessageBox,
    QCalendarWidget,  QMenu, QFileDialog, QLineEdit, QDialog
)
from PySide6.QtCore import Qt, QSize, QTimer, QThread, QDate
from fpdf import FPDF
from utils.api_utils import fetch_data, post_data, update_data, delete_data


class EmailThread(QThread):
    """Thread for sending emails in the background using Mailgun."""
    def __init__(self, recipient, subject, body):
        super().__init__()
        self.recipient = recipient
        self.subject = subject
        self.body = body

    async def run(self):
        """Send email using Mailgun API."""
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{os.getenv('MAILGUN_DOMAIN')}/messages",
                auth=("api", os.getenv("MAILGUN_API_KEY")),
                data={
                    "from": f"Hospital Management System <noreply@{os.getenv('MAILGUN_DOMAIN')}>",
                    "to": self.recipient,
                    "subject": self.subject,
                    "html": self.body
                }
            )

            if response.status_code != 200:
                print(f"Failed to send email: {response.text}")
        except Exception as e:
            print(f"Failed to send email: {e}")


class ManageAppointments(QWidget):
    def __init__(self, user_role, user_id, token):
        super().__init__()
        self.user_role = user_role
        self.doctor_id = user_id
        self.token = token
        self.dark_mode = True  # Default to dark mode
        self.reminder_timer = QTimer()  # Timer for reminders
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute

        self.setWindowTitle("Appointments Dashboard")
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        max_width = screen_geometry.width() * 0.8  # 80% of screen width
        max_height = screen_geometry.height() * 0.8  # 80% of screen height
        
        self.resize(int(max_width), int(max_height))  # Set window size
        self.setMinimumSize(800, 600)  # Set a reasonable minimum size
        self.init_ui()
        self.load_appointments()

    def init_ui(self):
        """Initialize UI components."""
        self.layout = QHBoxLayout(self)

        # Sidebar Menu
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QFrame { background-color: #282a36; border-right: 2px solid #44475a; }
            QPushButton { background: #6272a4; padding: 10px; border-radius: 5px; color: white; }
            QPushButton:hover { background: #50fa7b; color: black; }
        """)

        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(15)

        self.title_label = QLabel("📅 Appointments")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.sidebar_layout.addWidget(self.title_label)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_appointments)
        self.sidebar_layout.addWidget(self.refresh_btn)

        self.toggle_theme_btn = QPushButton("🌙 Light Mode")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        self.sidebar_layout.addWidget(self.toggle_theme_btn)

        self.export_btn = QPushButton("📤 Export Appointments")
        self.export_btn.clicked.connect(self.export_appointments)
        self.sidebar_layout.addWidget(self.export_btn)

        self.sidebar_layout.addStretch()
        self.layout.addWidget(self.sidebar)

        # Main Content Area
        self.main_frame = QFrame()
        self.main_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout(self.main_frame)

        self.header_label = QLabel("📋 Scheduled Appointments")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)

        # Search and Filter Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search appointments...")
        self.search_bar.textChanged.connect(self.filter_appointments)
        self.main_layout.addWidget(self.search_bar)

        self.appointment_list = QListWidget()
        self.appointment_list.setStyleSheet("""
            QListWidget { background-color: #44475a; border: none; font-size: 14px; color: white; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #6272a4; }
            QListWidget::item:selected { background-color: #50fa7b; color: black; }
        """)
        self.appointment_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.appointment_list.customContextMenuRequested.connect(self.show_context_menu)
        self.main_layout.addWidget(self.appointment_list)

        # Appointment Form Section
        self.form_frame = QFrame()
        self.form_frame.setStyleSheet("background: #282a36; padding: 15px; border-radius: 10px;")
        self.form_layout = QVBoxLayout(self.form_frame)

        self.form_title = QLabel("➕ Schedule Appointment")
        self.form_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.form_layout.addWidget(self.form_title)

        self.patient_dropdown = QComboBox()
        self.patient_dropdown.setPlaceholderText("Select a Patient")
        self.load_patients()
        self.patient_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px; color: white;")
        self.form_layout.addWidget(self.patient_dropdown)

        if self.user_role == "nurse":
            self.doctor_dropdown = QComboBox()
            self.doctor_dropdown.setPlaceholderText("Select a Doctor")
            self.load_doctors()
            self.doctor_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px; color: white;")
            self.form_layout.addWidget(self.doctor_dropdown)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px; color: white;")
        self.form_layout.addWidget(self.calendar_widget)

        self.hour_dropdown = QComboBox()
        self.hour_dropdown.setPlaceholderText("Select Hour")
        self.hour_dropdown.addItems([f"{h:02d}" for h in range(24)])
        self.hour_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px; color: white;")
        self.form_layout.addWidget(self.hour_dropdown)

        self.minute_dropdown = QComboBox()
        self.minute_dropdown.setPlaceholderText("Select Minute")
        self.minute_dropdown.addItems([f"{m:02d}" for m in range(0, 60, 15)])
        self.minute_dropdown.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px; color: white;")
        self.form_layout.addWidget(self.minute_dropdown)

        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Enter reason for appointment...")
        self.reason_input.setStyleSheet("background: #6272a4; padding: 5px; border-radius: 5px; color: white;")
        self.form_layout.addWidget(self.reason_input)

        self.schedule_button = QPushButton("📌 Schedule")
        self.schedule_button.setStyleSheet("background: #50fa7b; padding: 8px; border-radius: 5px; color: black;")
        self.schedule_button.clicked.connect(self.schedule_appointment)
        self.form_layout.addWidget(self.schedule_button)

        self.main_layout.addWidget(self.form_frame)
        self.layout.addWidget(self.main_frame)

        self.setLayout(self.layout)

    def load_patients(self):
        """Load patients into dropdown."""
        if self.user_role == "doctor":
            api_url = f"{os.getenv('ASSIGNED_PATIENTS_URL')}/{self.doctor_id}/patients"
        else:
            api_url = os.getenv('PATIENT_LIST_URL')

        patients = fetch_data(self, api_url, self.token)
        self.patient_dropdown.clear()

        if patients:
            for patient in patients:
                self.patient_dropdown.addItem(f"{patient['full_name']} (ID: {patient['id']})", patient["id"])

    def load_doctors(self):
        """Load doctors into dropdown."""
        api_url = os.getenv('DOCTOR_LIST_URL')
        doctors = fetch_data(self, api_url, self.token)
        self.doctor_dropdown.clear()

        if doctors:
            for doctor in doctors:
                self.doctor_dropdown.addItem(f"{doctor['full_name']} (ID: {doctor['id']})", doctor["id"])

    def load_appointments(self):
        """Load and display appointments."""
        if self.user_role == "doctor":
            api_url = f"{os.getenv('APPOINTMENTS_URL')}doctor/{self.doctor_id}/"
        else:
            api_url = os.getenv('APPOINTMENTS_URL')

        appointments = fetch_data(self, api_url, self.token)
        self.appointment_list.clear()

        if appointments:
            for appointment in appointments:
                item = QListWidgetItem(
                    f"{appointment['id']:<14}   {appointment['patient_name']:<25}   {appointment['datetime']:<25}   {appointment['status']}"
                )
                item.setData(Qt.UserRole, appointment)
                item.setSizeHint(QSize(0, 50))
                self.appointment_list.addItem(item)
        else:
            no_data_item = QListWidgetItem("No appointments scheduled.")
            no_data_item.setFlags(Qt.NoItemFlags)
            self.appointment_list.addItem(no_data_item)

    def filter_appointments(self):
        """Filter appointments based on search text."""
        search_text = self.search_bar.text().lower()
        for row in range(self.appointment_list.count()):
            item = self.appointment_list.item(row)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def show_context_menu(self, position):
        """Show context menu for appointment actions."""
        item = self.appointment_list.itemAt(position)
        if not item:
            return

        menu = QMenu()
        update_action = menu.addAction("📝 Mark as Completed")
        reschedule_action = menu.addAction("⏳ Reschedule")
        cancel_action = menu.addAction("❌ Cancel")
        delete_action = menu.addAction("🗑️ Delete")

        action = menu.exec_(self.appointment_list.mapToGlobal(position))
        appointment = item.data(Qt.UserRole)

        if action == update_action:
            self.update_appointment(appointment)
        elif action == reschedule_action:
            self.reschedule_appointment(appointment)
        elif action == cancel_action:
            self.cancel_appointment(appointment)
        elif action == delete_action:
            self.delete_appointment(appointment)

    def schedule_appointment(self):
        """Schedule a new appointment."""
        patient_text = self.patient_dropdown.currentText()
        match = re.match(r"(.+) \(ID: (\d+)\)", patient_text)

        if not match:
            QMessageBox.warning(self, "Error", "Invalid patient selection.")
            return

        patient_name = match.group(1)
        patient_id = int(match.group(2))

        selected_date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        selected_time = f"{self.hour_dropdown.currentText()}:{self.minute_dropdown.currentText()}:00"
        datetime_str = f"{selected_date} {selected_time}"

        reason = self.reason_input.toPlainText().strip()
        if not reason:
            QMessageBox.warning(self, "Error", "Enter a reason!")
            return

        if self.user_role == "doctor":
            doctor_id = self.doctor_id
        else:
            doctor_text = self.doctor_dropdown.currentText()
            match = re.match(r"(.+) \(ID: (\d+)\)", doctor_text)
            if not match:
                QMessageBox.warning(self, "Error", "Invalid doctor selection.")
                return
            doctor_id = int(match.group(2))

        api_url = os.getenv('APPOINTMENTS_URL')
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
            self.send_notification(patient_id, doctor_id, datetime_str, reason, "Scheduled")
        else:
            QMessageBox.critical(self, "Error", "Failed to schedule appointment.")
    
    def update_appointment(self, appointment):
        """Mark an appointment as completed."""
        confirm = QMessageBox.question(self, "Confirm Update", "Mark this appointment as completed?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        api_url = f"{os.getenv('APPOINTMENTS_URL')}{appointment['id']}/update"
        data = {"status": "Completed"}

        if update_data(self, api_url, data, self.token):
            QMessageBox.information(self, "Success", "Appointment marked as completed.")
            self.load_appointments()
            self.send_notification(appointment["patient_id"], appointment["doctor_id"], appointment["datetime"], appointment["reason"], "Completed")
        else:
            QMessageBox.critical(self, "Error", "Failed to update appointment.")


    def reschedule_appointment(self, appointment):
        """Reschedule an appointment."""
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

            api_url = f"{os.getenv('APPOINTMENTS_URL')}{appointment['id']}/reschedule"
            data = {
                "datetime": new_datetime,
                "status": "Rescheduled"
            }

            if update_data(self, api_url, data, self.token):
                QMessageBox.information(self, "Success", "Appointment rescheduled successfully.")
                self.load_appointments()
                self.send_notification(appointment["patient_id"], appointment["doctor_id"], new_datetime, appointment["reason"], "Rescheduled")
            else:
                QMessageBox.critical(self, "Error", "Failed to reschedule appointment.")


    def cancel_appointment(self, appointment):
        """Cancel an appointment."""
        confirm = QMessageBox.question(self, "Confirm Cancellation", "Are you sure you want to cancel this appointment?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        api_url = f"{os.getenv('APPOINTMENTS_URL')}{appointment['id']}/update"
        data = {"status": "Canceled"}

        if update_data(self, api_url, data, self.token):
            QMessageBox.information(self, "Success", "Appointment canceled.")
            self.load_appointments()
            self.send_notification(appointment["patient_id"], appointment["doctor_id"], appointment["datetime"], appointment["reason"], "Canceled")
        else:
            QMessageBox.critical(self, "Error", "Failed to cancel appointment.")


    def delete_appointment(self, appointment):
        """Delete an appointment."""
        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete this appointment?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return

        api_url = f"{os.getenv('APPOINTMENTS_URL')}{appointment['id']}"

        if delete_data(self, api_url, self.token):
            QMessageBox.information(self, "Success", "Appointment deleted.")
            self.load_appointments()
            self.send_notification(appointment["patient_id"], appointment["doctor_id"], appointment["datetime"], appointment["reason"], "Deleted")
        else:
            QMessageBox.critical(self, "Error", "Failed to delete appointment.")

    def send_notification(self, patient_id, doctor_id, datetime_str, reason, status):
        """Send professional email notifications to patient and doctor using Mailgun."""
        # Fetch patient email
        patient_email = self.get_patient_email(patient_id)
        if not patient_email:
            print("Failed to fetch patient email.")
            return

        # Fetch doctor email
        doctor_email = self.get_doctor_email(doctor_id)
        if not doctor_email:
            print("Failed to fetch doctor email.")
            return

        # Email subject
        subject = f"Appointment {status} - Hospital Management System"
        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 8px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #ddd;
                }}
                .header h1 {{
                    color: #0073e6;
                    margin: 0;
                }}
                .content {{
                    padding: 20px 0;
                }}
                .content p {{
                    margin: 10px 0;
                    line-height: 1.6;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 12px;
                    color: #777;
                }}
                .footer a {{
                    color: #0073e6;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>Hospital Management System</h1>
                </div>
                <div class="content">
                    <h2>Appointment {status}</h2>
                    <p><strong>Date/Time:</strong> {datetime_str}</p>
                    <p><strong>Reason:</strong> {reason}</p>
                    <p><strong>Status:</strong> {status}</p>
                    <p>Thank you for using our services. If you have any questions or need further assistance, please contact us at <a href="mailto:support@hospital.com">support@hospital.com</a>.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2023 Hospital Management System. All rights reserved.</p>
                    <p><a href="https://www.hospital.com">Visit our website</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        # Store EmailThread objects as instance variables
        self.patient_email_thread =  EmailThread(patient_email, subject, body)
        self.doctor_email_thread = EmailThread(doctor_email, subject, body)

        # Start the threads
        self.patient_email_thread.start()
        self.doctor_email_thread.start()

    def closeEvent(self, event):
        """Ensure all threads are finished before closing the application."""
        if hasattr(self, 'patient_email_thread') and self.patient_email_thread.isRunning():
            self.patient_email_thread.quit()
            self.patient_email_thread.wait()

        if hasattr(self, 'doctor_email_thread') and self.doctor_email_thread.isRunning():
            self.doctor_email_thread.quit()
            self.doctor_email_thread.wait()

        event.accept()

    def get_patient_email(self, patient_id):
        """Fetch patient email from the database."""
        api_url = f"{os.getenv('PATIENT_LIST_URL')}{patient_id}"
        patient = fetch_data(self, api_url, self.token)
        return patient.get("email") if patient else None

    def get_doctor_email(self, doctor_id):
        """Fetch doctor email from the database."""
        api_url = f"{os.getenv('DOCTOR_LIST_URL')}{doctor_id}"
        doctor = fetch_data(self, api_url, self.token)
        return doctor.get("email") if doctor else None

    def check_reminders(self):
        """Check for upcoming appointments and send reminders."""
        appointments = fetch_data(self, os.getenv('APPOINTMENTS_URL'), self.token)
        if not appointments:
            return

        now = datetime.now()
        for appointment in appointments:
            try:
                appointment_time = datetime.strptime(appointment["datetime"], "%Y-%m-%dT%H:%M:%S")
                time_diff = appointment_time - now

                if timedelta(hours=24) > time_diff > timedelta(hours=23):
                    self.send_reminder(appointment, "24 hours")
                elif timedelta(hours=1) > time_diff > timedelta(minutes=59):
                    self.send_reminder(appointment, "1 hour")
            except ValueError as e:
                print(f"Error parsing datetime for appointment {appointment['id']}: {e}")

    def send_reminder(self, appointment, time_left):
        """Send reminder email."""
        patient_email = self.get_patient_email(appointment["patient_id"])
        doctor_email = self.get_doctor_email(appointment["doctor_id"])

        if not patient_email or not doctor_email:
            return

        subject = f"Appointment Reminder: {time_left} left"
        body = f"""
            <h2>Appointment Reminder</h2>
            <p><strong>Patient:</strong> {appointment['patient_name']}</p>
            <p><strong>Date/Time:</strong> {appointment['datetime']}</p>
            <p><strong>Reason:</strong> {appointment['reason']}</p>
            <p><strong>Time Left:</strong> {time_left}</p>
        """

        # Send to patient
        EmailThread(patient_email, subject, body).start()

        # Send to doctor
        EmailThread(doctor_email, subject, body).start()

    def export_appointments(self):
        """Export appointments to CSV or PDF."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Appointments", "", "CSV Files (*.csv);;PDF Files (*.pdf)", options=options)

        if file_path:
            if file_path.endswith(".csv"):
                self.export_to_csv(file_path)
            elif file_path.endswith(".pdf"):
                self.export_to_pdf(file_path)

    def export_to_csv(self, file_path):
        """Export appointments to CSV."""
        appointments = fetch_data(self, os.getenv('APPOINTMENTS_URL'), self.token)
        if not appointments:
            return

        with open(file_path, "w") as file:
            file.write("ID,Patient Name,Date/Time,Reason,Status\n")
            for appointment in appointments:
                file.write(f"{appointment['id']},{appointment['patient_name']},{appointment['datetime']},{appointment['reason']},{appointment['status']}\n")

        QMessageBox.information(self, "Success", "Appointments exported to CSV!")

    def export_to_pdf(self, file_path):
        """Export appointments to PDF."""
        appointments = fetch_data(self, os.getenv('APPOINTMENTS_URL'), self.token)
        if not appointments:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Appointments Report", ln=True, align="C")
        pdf.ln(10)

        for appointment in appointments:
            pdf.cell(200, 10, txt=f"ID: {appointment['id']}", ln=True)
            pdf.cell(200, 10, txt=f"Patient: {appointment['patient_name']}", ln=True)
            pdf.cell(200, 10, txt=f"Date/Time: {appointment['datetime']}", ln=True)
            pdf.cell(200, 10, txt=f"Reason: {appointment['reason']}", ln=True)
            pdf.cell(200, 10, txt=f"Status: {appointment['status']}", ln=True)
            pdf.ln(5)

        pdf.output(file_path)
        QMessageBox.information(self, "Success", "Appointments exported to PDF!")

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        if self.dark_mode:
            self.setStyleSheet("QWidget { background-color: white; color: black; }")
            self.toggle_theme_btn.setText("🌙 Dark Mode")
        else:
            self.setStyleSheet("QWidget { background-color: #1e1e2e; color: white; }")
            self.toggle_theme_btn.setText("☀️ Light Mode")

        self.dark_mode = not self.dark_mode