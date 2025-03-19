import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from core.auth import AuthHandler
from views.login import LoginScreen
from views.dashboard import Dashboard
from views.reset_password import ResetPasswordPage
from check_protocol import is_protocol_registered
from register_protocol import register_protocol
from urllib.parse import urlparse, parse_qs

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.auth_handler = AuthHandler()
        self.login_screen = LoginScreen(self.on_login_success)
        self.dashboard = None
        
        
        # Register the custom protocol if needed
        self.register_protocol_if_needed()

        # Check for a custom URL argument (e.g., hmsresetpass://reset-password?token=RESET_TOKEN)
        self.reset_token = self.get_reset_token_from_url()

        if self.reset_token:
            self.open_reset_password_page(self.reset_token)
        else:
            self.login_screen.show()

    def get_reset_token_from_url(self):
        """Extract the reset token from a custom URL argument."""
        args = sys.argv
        if len(args) > 1:
            url = args[1]  # The custom URL is passed as the second argument
            parsed_url = urlparse(url)
            if parsed_url.scheme == "hmsresetpass" and parsed_url.path == "reset-password":
                query_params = parse_qs(parsed_url.query)
                return query_params.get("token", [None])[0]
        return None

    def open_reset_password_page(self, token):
        """Open the ResetPasswordPage with the provided token."""
        self.reset_password_page = ResetPasswordPage(token)
        self.reset_password_page.show()
        
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
            
    def register_protocol_if_needed(self):
        """
        Check if the custom protocol is registered, and register it if necessary.
        """
        if not is_protocol_registered():
            register_protocol()
        

    def run(self):
        self.login_screen.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()