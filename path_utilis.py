import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller .exe - use user's AppData for data storage
        app_name = "BillManager"  # Change this to your app name
        user_data_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", app_name)
        os.makedirs(user_data_path, exist_ok=True)
        
        # Copy bundled data to user directory on first run (if needed)
        user_data_dir = os.path.join(user_data_path, 'data')
        if not os.path.exists(user_data_dir):
            bundled_data_dir = os.path.join(sys._MEIPASS, 'data')
            if os.path.exists(bundled_data_dir):
                import shutil
                shutil.copytree(bundled_data_dir, user_data_dir)
        
        return user_data_path
    # Running from .py source - use original location
    return os.path.dirname(os.path.abspath(__file__))