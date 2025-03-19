import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from core.auth import AuthHandler
from views.login import LoginScreen
from views.dashboard import Dashboard

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.auth_handler = AuthHandler()
        self.login_screen = LoginScreen(self.on_login_success)
        self.dashboard = None

    def on_login_success(self, role, user_id, token):
        try:
            if not role or not token or not user_id:  # Handle missing data
                raise ValueError("Role, token, or user ID is missing!")

            self.dashboard = Dashboard(role, user_id, token)
            self.dashboard.show()
            self.login_screen.close()
        except Exception as e:
            print("Login success failed!", {e})
            QMessageBox.critical(None, "Error", f"Login success failed: {e}")
   

    def run(self):
        self.login_screen.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()