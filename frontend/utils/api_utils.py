import os
import requests
from PySide6.QtWidgets import QMessageBox

def fetch_data(self, api_url, auth_token=None, params=None):
    """Generic function to fetch data from an API."""
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
                QMessageBox.critical(self,"Error", "Access forbidden. You don't have permission.")
        elif response.status_code == 401:
                QMessageBox.critical(self,"Error", "Unauthorized. Please log in again.")
        else:
                QMessageBox.critical(self,"Error", f"Failed to fetch data. Error {response.status_code}")
    except Exception as e:
        QMessageBox.critical(self, None, "Error", f"An error occurred: {e}")
        return None

def post_data(api_url, data, auth_token=None):
    """Generic function to post data to an API."""
    
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            return True
        else:
            QMessageBox.critical(None, "Error", f"Failed to post data to {api_url}")
            return False
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred: {e}")
        return False

def update_data(api_url, data, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.put(api_url, json=data, headers=headers)
        if response.status_code in [200, 201]:
            return True
        else:
            QMessageBox.critical(None, "Error", f"Failed to update data to {api_url}")
            return False
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred: {e}")
        return False