from PySide6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
import requests

class ChangePasswordWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Change Password")

        layout = QVBoxLayout()

        self.current_password_label = QLabel("Current Password:")
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)

        self.new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_label = QLabel("Confirm New Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.submit_button = QPushButton("Change Password")
        self.submit_button.clicked.connect(self.change_password)

        layout.addWidget(self.current_password_label)
        layout.addWidget(self.current_password_input)
        layout.addWidget(self.new_password_label)
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.submit_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def change_password(self):
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "New passwords do not match!")
            return

        response = requests.post(
            "http://127.0.0.1:8000/auth/change-password",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"current_password": current_password, "new_password": new_password},
        )

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Password changed successfully!")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Failed to change password. Check your current password.")
