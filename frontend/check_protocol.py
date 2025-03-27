import winreg

def is_protocol_registered():
    """
    Check if the custom protocol (hmsresetpass://) is registered in the Windows Registry.
    """
    try:
        # Open the protocol key
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"hmsresetpass") as key:
            # Check if the "URL Protocol" value exists
            winreg.QueryValueEx(key, "URL Protocol")
            return True  # Protocol is registered
    except FileNotFoundError:
        return False  # Protocol is not registered
    except Exception as e:
        print(f"Error checking protocol registration: {e}")
        return False