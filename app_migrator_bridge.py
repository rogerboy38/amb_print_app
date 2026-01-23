"""
Bridge between amb_print_app and app_migrator
Automates print format migration to ERPNext
"""

import json
import requests
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class AppMigratorBridge:
    """Bridge for app_migrator integration"""
    
    def __init__(self):
        self.erpnext_url = os.getenv("ERPNEXT_URL")
        self.api_key = os.getenv("ERPNEXT_API_KEY")
        self.api_secret = os.getenv("ERPNEXT_API_SECRET")
        self.config_file = Path("data/migrator_config.json")
    
    def load_config(self):
        """Load migration configuration"""
        with open(self.config_file, "r") as f:
            return json.load(f)
    
    def validate_setup(self):
        """Validate integration setup"""
        checks = {
            "ERPNext URL": bool(self.erpnext_url),
            "API Key": bool(self.api_key),
            "API Secret": bool(self.api_secret),
            "Config File": self.config_file.exists()
        }
        
        print("🔍 Integration Setup Check:")
        for check, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {check}")
        
        return all(checks.values())
    
    def create_print_format(self, format_config):
        """Create print format via ERPNext API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}:{self.api_secret}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "doctype": "Print Format",
            "name": format_config["name"],
            "doc_type": "Document",
            "module": format_config.get("module", "Custom"),
            "print_format_type": format_config.get("template_type", "Jinja"),
            "enabled": 1
        }
        
        url = f"{self.erpnext_url}/api/resource/Print Format"
        
        try:
            response = requests.post(url, json=payload, headers=headers, verify=False)
            if response.status_code in [200, 201]:
                print(f"✅ Created: {format_config['name']}")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def migrate(self):
        """Execute migration"""
        print("🚀 Starting app_migrator Bridge Migration")
        print("=========================================")
        print()
        
        # Validate
        if not self.validate_setup():
            print("\n❌ Setup validation failed!")
            return False
        
        print()
        
        # Load config
        config = self.load_config()
        print(f"📋 Loaded config with {len(config['print_formats'])} print formats")
        
        # Migrate each format
        success_count = 0
        for format_config in config["print_formats"]:
            if self.create_print_format(format_config):
                success_count += 1
        
        print()
        print(f"✅ Migration Complete: {success_count}/{len(config['print_formats'])} successful")
        
        return success_count == len(config["print_formats"])

if __name__ == "__main__":
    bridge = AppMigratorBridge()
    bridge.migrate()



# chmod +x app_migrator_bridge.py  # Commented out - shell command
