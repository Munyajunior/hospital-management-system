
class LoadAuthCred():
    def load_auth_token(self):
        """Load authentication token stored after login"""
        try:
            with open("auth_token.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    def load_user_id(self):
        """Load authenticated user_id stored after login"""
        try:
            with open("user_id.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None