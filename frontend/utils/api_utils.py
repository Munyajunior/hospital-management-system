import os
import requests
from PySide6.QtWidgets import QMessageBox

def fetch_data(self, api_url, auth_token=None, params=None):
    """Generic function to fetch data from an API."""
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.get(api_url, headers=headers, params=params)
        print("Backend response:", response.status_code, response.text)  # Debugging line
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
                QMessageBox.critical(self,"Error", f"Access forbidden. You don't have permission. {response.text}")
        elif response.status_code == 401:
                QMessageBox.critical(self,"Error", f"Unauthorized. Please log in again.\n {response.text}")
        else:
                QMessageBox.critical(self,"Error", f"Failed to fetch data. Error {response.text}")
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        return None

def post_data(self, api_url, data, auth_token=None):
    """Generic function to post data to an API."""
    
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.post(api_url, json=data, headers=headers)
        print("Backend response:", response.status_code, response.text)  # Debugging line
        
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 403:
                QMessageBox.critical(self,"Error", f"Access forbidden. You don't have permission. {response.text}")
        elif response.status_code == 401:
                QMessageBox.critical(self,"Error", f"Unauthorized. Please log in again.\n {response.text}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to post data {response.text}")
            return False
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        return False

def update_data(self, api_url, data, auth_token=None):
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.put(api_url, json=data, headers=headers)
        print("Backend response:", response.status_code, response.text)  # Debugging line
        
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 403:
                QMessageBox.critical(self,"Error", f"Access forbidden. You don't have permission. {response.text}")
        elif response.status_code == 401:
                QMessageBox.critical(self,"Error", f"Unauthorized. Please log in again.\n {response.text}")
                self.close()
        else:
            QMessageBox.critical(self, "Error", f"Failed to update data {response.text}")
            return False
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        return False
    

def delete_data(self, api_url, auth_token=None, params=None):
    """Generic function to delete data from an API."""
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    try:
        response = requests.delete(api_url, headers=headers, params=params)
        print("Backend response:", response.status_code, response.text)  # Debugging line
        
        if response.status_code == 204:  
            return True 
        elif response.status_code == 403:
            QMessageBox.critical(self, "Error", f"Access forbidden. You don't have permission. {response.text}")
        elif response.status_code == 401:
            QMessageBox.critical(self,"Error", f"Unauthorized. Please log in again.\n {response.text}")
        else:
            QMessageBox.critical(self, "Error", f"Failed to delete data. Error {response.text}")
        return False
    except Exception as e:
        QMessageBox.critical(self, "Error", f"An error occurred: {e}")
        return False
    