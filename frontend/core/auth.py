import os
import requests

class AuthHandler:
    def __init__(self):
        self.api_url = os.getenv("LOGIN_URL", "http://127.0.0.1:8000/api/auth/login")

    def authenticate(self, email, password):
        data = {"email": email, "password": password}
        try:
            response = requests.post(self.api_url, json=data)
            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                role = result.get("role")
                self.save_token(token)
                return True, "Login successful!", role
            return False, "Invalid credentials. Please try again.", None
        except requests.exceptions.RequestException:
            return False, "Unable to connect to the server.", None

    def save_token(self, token):
        with open("auth_token.txt", "w") as file:
            file.write(token)
