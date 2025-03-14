from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QWidget

class ProfileWindow(QMainWindow):
    def __init__(self, user_info, token):
        super().__init__()
        self.user_info = user_info
        self.token = token
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("User Profile")

        layout = QVBoxLayout()

        self.name_label = QLabel(f"Name: {self.user_info['name']}")
        self.email_label = QLabel(f"Email: {self.user_info['email']}")
        self.role_label = QLabel(f"Role: {self.user_info['role']}")

        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.clicked.connect(self.open_change_password)

        layout.addWidget(self.name_label)
        layout.addWidget(self.email_label)
        layout.addWidget(self.role_label)
        layout.addWidget(self.change_password_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_change_password(self):
        from .change_password import ChangePasswordWindow
        self.change_password_window = ChangePasswordWindow(self.token)
        self.change_password_window.show()
