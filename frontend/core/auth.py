import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AuthHandler:
    def __init__(self):
        self.api_url = os.getenv("LOGIN_URL")

    def authenticate(self, email, password):
        data = {"email": email, "password": password}
        try:
            response = requests.post(self.api_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                role = result.get("role")
                user_id = str(result.get("sub"))
                
                return True, "Login successful!", role, user_id, token
            elif response.status_code == 401:
                # Handle invalid credentials
                return False, "Invalid credentials. Please try again.", None, None, None
            else:
                return False, "An error occurred. Please try again later.", None, None, None
        except requests.exceptions.RequestException as e:
            return False, f"Unable to connect to the server: {str(e)}", None, None, None

    def save_token(self, token, role, user_id):
        with open("auth_token.txt", "w") as file:
            file.write(token)
        with open("role.txt", "w") as file:  
            file.write(role)
        with open("user_id.txt", "w") as file:  
            file.write(user_id)



