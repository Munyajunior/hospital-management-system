from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import requests

class ForgotPasswordPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Forgot Password")
        self.setGeometry(400, 200, 400, 250)

        layout = QVBoxLayout()

        self.label = QLabel("Enter your email to reset password:")
        layout.addWidget(self.label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.submit_button = QPushButton("Send Reset Link")
        self.submit_button.clicked.connect(self.send_reset_request)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def send_reset_request(self):
        email = self.email_input.text()
        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email!")
            return

        try:
            response = requests.post("http://localhost:8000/auth/forgot-password", json={"email": email})
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "A reset link has been sent to your email.")
                self.close()
            else:
                QMessageBox.warning(self, "Error", response.json().get("detail", "Something went wrong"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send request: {str(e)}")
