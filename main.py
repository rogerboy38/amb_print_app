#!/usr/bin/env python3
"""
AMB Print Application - Main Entry Point

A comprehensive Python-based PDF to ERPNext Print Format converter
with QtDesigner-based user interface.

Author: rogerboy38
Version: 1.0.0
"""

import sys
from pathlib import Path
from loguru import logger

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.ui.main_window import MainWindow


def setup_logging():
    """Configure logging for the application."""
    log_level = settings.LOG_LEVEL
    log_file = settings.LOG_DIR / "amb_print_app.log"
    
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    logger.info("Logging initialized")


def main():
    """Main application entry point."""
    try:
        logger.info("Starting AMB Print Application")
        setup_logging()
        
        # Initialize Qt Application
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("AMB Print Application")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AMB")
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Application window displayed")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
