"""
Generate app_migrator compatible configuration from amb_print_app
Bridge between amb_print_app and app_migrator
"""

import json
from pathlib import Path
from datetime import datetime

def generate_migrator_config():
    """Generate app_migrator configuration for print format migration"""
    
    config = {
        "migration_type": "print_format",
        "app": "amb_print_app",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "print_formats": [
            {
                "name": "COA - Certificate of Analysis",
                "doctype": "Print Format",
                "module": "Custom",
                "source_pdf": "pdf_files/COA TRUROOTS.pdf",
                "template_type": "Jinja",
                "standard": "No",
                "description": "Certificate of Analysis print format from TRUROOTS"
            },
            {
                "name": "COA - Batch 25-0004",
                "doctype": "Print Format",
                "module": "Custom",
                "source_pdf": "pdf_files/COA-25-0004.pdf",
                "template_type": "Jinja",
                "standard": "No",
                "description": "Certificate of Analysis print format for batch 25-0004"
            }
        ],
        "deployment": {
            "target_environment": "testprod",
            "url": "https://sysmayal.frappe.cloud",
            "auto_deploy": False
        },
        "hooks": {
            "before_migrate": "validate_pdf_extraction",
            "after_migrate": "verify_print_formats"
        }
    }
    
    # Save configuration
    output_file = Path("data/migrator_config.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration generated: {output_file}")
    print(json.dumps(config, indent=2))
    
    return config

if __name__ == "__main__":
    generate_migrator_config()

python generate_migrator_config.py
