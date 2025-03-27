import winreg
import os
import sys

def register_protocol():
    """
    Register the custom protocol (hmsresetpass://) in the Windows Registry using the `winreg` module.
    """
    try:
        # Get the path to the executable
        app_path = os.path.abspath(sys.executable)

        # Define the registry key for the custom protocol
        protocol_key = r"hmsresetpass"
        command_key = rf"{protocol_key}\shell\open\command"

        # Create the protocol key
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, protocol_key) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, "URL:hmsresetpass Protocol")
            winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")

        # Create the command key
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_key) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f'"{app_path}" "%1"')

        print("Custom protocol registered successfully.")
    except Exception as e:
        print(f"Failed to register custom protocol: {e}")