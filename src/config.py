"""
Configuration Module for AMB Print Application

Manages application settings, environment variables, and paths.
"""

from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
TESTS_DIR = PROJECT_ROOT / "tests"

# Create necessary directories
for directory in [DATA_DIR, LOG_DIR, TESTS_DIR]:
    directory.mkdir(exist_ok=True)


class Settings:
    """Application settings configuration."""
    
    # Application metadata
    APP_NAME = "AMB Print Application"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "rogerboy38"
    
    # Project paths
    PROJECT_ROOT = PROJECT_ROOT
    SRC_DIR = SRC_DIR
    DATA_DIR = DATA_DIR
    LOG_DIR = LOG_DIR
    TESTS_DIR = TESTS_DIR
    
    # Logging configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOG_DIR / "amb_print_app.log"
    LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    
    # PDF Processing settings
    PDF_MAX_SIZE_MB = 50  # Maximum PDF file size in MB
    PDF_TIMEOUT_SECONDS = 300  # Timeout for PDF processing
    SUPPORTED_PDF_VERSIONS = ["1.4", "1.5", "1.6", "1.7"]  # Supported PDF versions
    
    # ERPNext API settings
    ERPNEXT_URL = os.getenv("ERPNEXT_URL", "http://localhost:8000")
    ERPNEXT_API_KEY = os.getenv("ERPNEXT_API_KEY", "")
    ERPNEXT_API_SECRET = os.getenv("ERPNEXT_API_SECRET", "")
    ERPNEXT_TIMEOUT = 30  # API request timeout in seconds
    
    # UI settings
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 900
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    THEME = os.getenv("THEME", "light")
    
    # Template generation settings
    OUTPUT_FORMAT = "html"  # html or json
    JINJA_AUTOESCAPE = True
    DEFAULT_FONT = "Arial"
    DEFAULT_FONT_SIZE = 12
    
    # Performance settings
    THREAD_POOL_SIZE = 4
    CACHE_ENABLED = True
    CACHE_MAX_SIZE_MB = 100
    
    # Feature flags
    ENABLE_AI_DETECTION = os.getenv("ENABLE_AI_DETECTION", "False").lower() == "true"
    ENABLE_AUTO_SAVE = os.getenv("ENABLE_AUTO_SAVE", "True").lower() == "true"
    ENABLE_PREVIEW = True
    
    @classmethod
    def get_setting(cls, key: str, default: Optional[str] = None) -> str:
        """Get a setting value with fallback to default."""
        return os.getenv(key, getattr(cls, key, default))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical settings."""
        required_settings = [
            "APP_NAME",
            "PROJECT_ROOT",
            "LOG_DIR",
        ]
        
        for setting in required_settings:
            if not getattr(cls, setting, None):
                raise ValueError(f"Required setting '{setting}' is not configured")
        
        return True


# Singleton instance
settings = Settings()

# Validate settings on import
settings.validate()
