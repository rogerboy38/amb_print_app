#!/usr/bin/env python
"""
API Upload Script for Print Formats
Uploads migrated print formats to ERPNext via REST API.
Supports both sandbox and production environments.
"""

import requests
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Configure logging
log_file = f"api_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ERPNextAPIClient:
    """Client for interacting with ERPNext REST API."""
    
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        """
        Initialize ERPNext API client.
        
        Args:
            base_url: Base URL of ERPNext instance (e.g., https://sysmayal.frappe.cloud)
            api_key: API key for authentication
            api_secret: API secret for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_key}:{api_secret}"
        }
    
    def upload_print_format(self, print_format_data: Dict) -> Tuple[bool, str]:
        """
        Upload a single print format to ERPNext.
        
        Args:
            print_format_data: Dictionary containing print format details
        
        Returns:
            Tuple[bool, str]: (success, response_message)
        """
        endpoint = f"{self.base_url}/api/resource/Print Format"
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps(print_format_data),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Successfully uploaded: {print_format_data.get('name', 'Unknown')}")
                return True, response.json()
            else:
                error_msg = f"Failed to upload {print_format_data.get('name')}: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg
        
        except requests.exceptions.Timeout:
            error_msg = f"Timeout uploading {print_format_data.get('name')}"
            logger.error(error_msg)
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error uploading {print_format_data.get('name')}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error uploading {print_format_data.get('name')}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def batch_upload(self, formats_file: str) -> Dict:
        """
        Upload multiple print formats from a JSON file.
        
        Args:
            formats_file: Path to JSON file containing print format array
        
        Returns:
            Dict with upload statistics
        """
        stats = {"total": 0, "success": 0, "failed": 0, "errors": []}
        
        try:
            with open(formats_file, 'r') as f:
                formats = json.load(f)
            
            if not isinstance(formats, list):
                formats = [formats]
            
            stats["total"] = len(formats)
            logger.info(f"\n=== Starting batch upload of {stats['total']} formats ===")
            
            for i, format_data in enumerate(formats, 1):
                logger.info(f"\n[{i}/{stats['total']}] Processing: {format_data.get('name', 'Unknown')}")
                success, response = self.upload_print_format(format_data)
                
                if success:
                    stats["success"] += 1
                else:
                    stats["failed"] += 1
                    stats["errors"].append({"format": format_data.get('name'), "error": response})
            
            logger.info(f"\n=== Batch upload complete ===")
            logger.info(f"Success: {stats['success']}/{stats['total']}")
            logger.info(f"Failed: {stats['failed']}/{stats['total']}")
            
            return stats
        
        except FileNotFoundError:
            logger.error(f"File not found: {formats_file}")
            stats["errors"].append({"file": formats_file, "error": "File not found"})
            return stats
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {formats_file}: {str(e)}")
            stats["errors"].append({"file": formats_file, "error": f"JSON decode error: {str(e)}"})
            return stats
        except Exception as e:
            logger.error(f"Error reading {formats_file}: {str(e)}")
            stats["errors"].append({"file": formats_file, "error": str(e)})
            return stats


def load_credentials(credentials_file: str) -> Dict:
    """Load API credentials from JSON file."""
    try:
        with open(credentials_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Credentials file not found: {credentials_file}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in credentials file: {credentials_file}")
        raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Upload print formats to ERPNext via REST API"
    )
    parser.add_argument(
        '--env',
        choices=['sandbox', 'production'],
        default='sandbox',
        help='Target environment (default: sandbox)'
    )
    parser.add_argument(
        '--formats-file',
        required=True,
        help='JSON file containing print formats to upload'
    )
    parser.add_argument(
        '--credentials-file',
        default='config/credentials.json',
        help='Path to credentials file (default: config/credentials.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load credentials
        credentials = load_credentials(args.credentials_file)
        env_config = credentials.get(args.env, {})
        
        if not env_config:
            logger.error(f"No configuration found for environment: {args.env}")
            sys.exit(1)
        
        # Initialize API client
        client = ERPNextAPIClient(
            base_url=env_config['base_url'],
            api_key=env_config['api_key'],
            api_secret=env_config['api_secret']
        )
        
        # Perform batch upload
        stats = client.batch_upload(args.formats_file)
        
        # Exit with appropriate code
        sys.exit(0 if stats["failed"] == 0 else 1)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
