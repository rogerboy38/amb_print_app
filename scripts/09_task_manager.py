#!/usr/bin/env python3
"""
09_task_manager.py - Unified Task Manager for AMB Print App

This orchestrator manages all batch processing tasks including:
  - PDF archive analysis and validation
  - Batch migration with enhanced debugging
  - API-based format uploads
  - End-to-end orchestration of the complete pipeline

Author: AMB Print App Development Team
Date: 2025
"""

import subprocess
import sys
import os
import logging
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define paths
SCRIPT_PATH = Path(__file__).parent.resolve()

SCRIPTS = {
    "debug": "07_batch_migration_debug.py",
    "upload": "06_api_upload.py",
    "orchestrator": "08_phase4_orchestrator.py"
}

class TaskManager:
    """Manages and orchestrates all batch processing tasks."""
    
    def __init__(self):
        self.task_history = []
        self.success_count = 0
        self.failure_count = 0
    
    def run_script(self, script_name: str, *args) -> Dict:
        """Execute a script with error handling and logging."""
        if script_name not in SCRIPTS:
            logger.error(f"Unknown script: {script_name}")
            return {"status": "error", "message": f"Unknown script: {script_name}"}
        
        script_file = SCRIPT_PATH / SCRIPTS[script_name]
        if not script_file.exists():
            logger.error(f"Script not found: {script_file}")
            return {"status": "error", "message": f"Script not found: {script_file}"}
        
        cmd = [sys.executable, str(script_file)] + list(args)
        logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            output = {
                "script": script_name,
                "status": "success" if result.returncode == 0 else "error",
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
            if result.returncode == 0:
                self.success_count += 1
                logger.info(f"{script_name} completed successfully")
            else:
                self.failure_count += 1
                logger.error(f"{script_name} failed with return code {result.returncode}")
            
            self.task_history.append(output)
            return output
        
        except subprocess.TimeoutExpired:
            logger.error(f"{script_name} timed out after 300 seconds")
            return {"status": "error", "message": "Script timeout"}
        except Exception as e:
            logger.error(f"Error running {script_name}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def run_debug(self) -> Dict:
        """Run debug migration script to analyze PDF archives."""
        logger.info("Starting debug migration analysis...")
        return self.run_script("debug")
    
    def run_upload(self) -> Dict:
        """Run API upload script to push formats via API."""
        logger.info("Starting API upload process...")
        return self.run_script("upload")
    
    def run_orchestrator(self) -> Dict:
        """Run orchestrator for full batch pipeline processing."""
        logger.info("Starting orchestrator pipeline...")
        return self.run_script("orchestrator")
    
    def run_full_pipeline(self) -> Dict:
        """Execute the complete pipeline: debug → upload → orchestrate."""
        logger.info("="*60)
        logger.info("Starting FULL PIPELINE execution")
        logger.info("="*60)
        
        results = {
            "pipeline": "full",
            "start_time": datetime.now().isoformat(),
            "stages": {}
        }
        
        # Stage 1: Debug
        logger.info("\nStage 1/3: Debug Migration Analysis")
        results["stages"]["debug"] = self.run_debug()
        
        # Check if debug succeeded before proceeding
        if results["stages"]["debug"]["status"] == "error":
            logger.warning("Debug stage failed, but continuing to next stage...")
        
        # Stage 2: Upload
        logger.info("\nStage 2/3: API Upload Process")
        results["stages"]["upload"] = self.run_upload()
        
        # Stage 3: Orchestrator
        logger.info("\nStage 3/3: Orchestrator Pipeline")
        results["stages"]["orchestrator"] = self.run_orchestrator()
        
        results["end_time"] = datetime.now().isoformat()
        results["summary"] = {
            "total_tasks": len(results["stages"]),
            "successful": self.success_count,
            "failed": self.failure_count
        }
        
        logger.info("\n" + "="*60)
        logger.info(f"Pipeline Summary: {results['summary']}")
        logger.info("="*60)
        
        return results
    
    def print_menu(self):
        """Display interactive menu."""
        print("\n" + "="*60)
        print("AMB Print App - Unified Task Manager")
        print("="*60)
        print("1. Run Debug Migration Script")
        print("2. Run API Upload Script")
        print("3. Run Orchestrator Script")
        print("4. Run Full Pipeline (All Stages)")
        print("5. View Task History")
        print("0. Exit")
        print("="*60)
    
    def show_history(self):
        """Display task execution history."""
        if not self.task_history:
            print("\nNo tasks executed yet.")
            return
        
        print("\n" + "="*60)
        print("Task Execution History")
        print("="*60)
        for i, task in enumerate(self.task_history, 1):
            print(f"\n{i}. {task.get('script', 'Unknown')} - {task.get('timestamp', 'Unknown')}")
            print(f"   Status: {task.get('status', 'Unknown')}")
            print(f"   Return Code: {task.get('return_code', 'N/A')}")
            if task.get('stderr'):
                print(f"   Error: {task['stderr'][:100]}...")
        print("\n" + "="*60)
    
    def interactive_menu(self):
        """Run interactive command menu."""
        while True:
            self.print_menu()
            choice = input("Choose an action (0-5): ").strip()
            
            if choice == "1":
                self.run_debug()
            elif choice == "2":
                self.run_upload()
            elif choice == "3":
                self.run_orchestrator()
            elif choice == "4":
                self.run_full_pipeline()
            elif choice == "5":
                self.show_history()
            elif choice == "0":
                logger.info("Exiting task manager.")
                break
            else:
                print("Invalid option. Please select 0-5.")


def main():
    """Main entry point."""
    manager = TaskManager()
    
    if len(sys.argv) > 1:
        # Command-line mode
        command = sys.argv[1]
        args = sys.argv[2:]
        
        if command == "debug":
            manager.run_debug()
        elif command == "upload":
            manager.run_upload()
        elif command == "orchestrator":
            manager.run_orchestrator()
        elif command == "pipeline":
            manager.run_full_pipeline()
        else:
            logger.error(f"Unknown command: {command}")
            print("Usage: python 09_task_manager.py [debug|upload|orchestrator|pipeline]")
            sys.exit(1)
    else:
        # Interactive mode
        manager.interactive_menu()


if __name__ == "__main__":
    main()
