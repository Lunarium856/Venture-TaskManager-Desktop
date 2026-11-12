import os, json

class Settings:
    def __init__(self, controller=None):
        self.controller = controller
        
        # Locate client/data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))  # client/core
        client_dir = os.path.dirname(current_dir)                 # client
        self.data_dir = os.path.join(client_dir, "data")
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.data = self.load_settings()

    def load_settings(self):
        """Loads settings from JSON, or creates default settings if file is missing."""
        default_settings = {
            "theme": "Venture",
            "window": {
                "width": 1200,
                "height": 800,
                "maximized": True
            },
            "preferences": {
                "auto_sync": True
            }
        }
        
        if not os.path.exists(self.settings_file):
            self.save_all(default_settings)
            return default_settings
            
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default_settings

    def save_all(self, data):
        """Writes the complete settings dictionary to JSON."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def value(self, key_path, default=None):
        """Retrieves a value using dot notation or slash notation (e.g., 'theme' or 'window/width')."""
        keys = key_path.replace("\\", "/").split("/")
        val = self.data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def setValue(self, key_path, value):
        """
        Sets a value using slash notation & immediately persists to JSON.
        """
        keys = key_path.replace("\\", "/").split("/")
        d = self.data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self.save_all(self.data)