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

    def on_login_success(self, role):
        try:
            with open("auth_token.txt", "r") as file:
                auth_token = file.read().strip()
            with open("role.txt", "r") as file:
                role = file.read().strip()
            with open("user_id.txt", "r") as file:
                user_id = file.read().strip()

            if not role or not auth_token:  # Handle missing data
                raise ValueError("Role or token is missing!")

            self.dashboard = Dashboard(role, user_id, auth_token)
            self.dashboard.show()
            self.login_screen.close()
        
        except Exception as e:
            print(f"Error during login success: {e}")
            QMessageBox.critical(None, "Error", f"Login success failed: {e}")


    def run(self):
        self.login_screen.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()