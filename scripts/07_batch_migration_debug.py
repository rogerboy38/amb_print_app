#!/usr/bin/env python
"""
Batch Migration Debug Utility
Provides enhanced logging and error handling for batch PDF-to-format migration.
Generates detailed reports for troubleshooting and validation.
"""

import logging
import json
import sys
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import subprocess


class MigrationDebugger:
    """Enhanced debugging and logging for batch migration processes."""
    
    def __init__(self, output_dir: str = 'migration_debug_logs'):
        """
        Initialize the migration debugger.
        
        Args:
            output_dir: Directory for storing debug logs and reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.output_dir / f'migration_debug_{timestamp}.log'
        self.error_file = self.output_dir / f'migration_errors_{timestamp}.log'
        self.report_file = self.output_dir / f'migration_report_{timestamp}.json'
        
        # Configure logger
        self.logger = logging.getLogger('MigrationDebugger')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler - debug log
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.DEBUG)
        
        # File handler - errors only
        eh = logging.FileHandler(self.error_file)
        eh.setLevel(logging.ERROR)
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
        fh.setFormatter(formatter)
        eh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(eh)
        self.logger.addHandler(ch)
        
        # Statistics tracking
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'warnings': 0,
            'errors_by_type': defaultdict(int),
            'processing_times': [],
            'failed_files': [],
            'edge_cases': []
        }
    
    def log_file_processing(self, filename: str, status: str, details: Dict[str, Any] = None):
        """
        Log file processing status with details.
        
        Args:
            filename: Name of the file being processed
            status: 'START', 'SUCCESS', 'FAILED', 'WARNING'
            details: Optional dictionary with additional details
        """
        if status == 'START':
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing: {filename}")
            self.logger.info(f"{'='*60}")
        elif status == 'SUCCESS':
            self.logger.info(f"✓ COMPLETED: {filename}")
            self.stats['success'] += 1
        elif status == 'FAILED':
            self.logger.error(f"✗ FAILED: {filename}")
            self.stats['failed'] += 1
            self.stats['failed_files'].append(filename)
        elif status == 'WARNING':
            self.logger.warning(f"⚠ WARNING: {filename}")
            self.stats['warnings'] += 1
        
        if details:
            self.logger.debug(f"Details: {json.dumps(details, indent=2)}")
    
    def log_edge_case(self, filename: str, case_type: str, description: str):
        """
        Log detected edge cases for later analysis.
        
        Args:
            filename: File with edge case
            case_type: Type of edge case (e.g., 'missing_field', 'format_anomaly')
            description: Description of the edge case
        """
        edge_case = {
            'file': filename,
            'type': case_type,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        self.stats['edge_cases'].append(edge_case)
        self.logger.warning(f"Edge case detected: {case_type} - {description}")
    
    def log_error_with_context(self, filename: str, error: Exception, context: Dict[str, Any] = None):
        """
        Log error with full traceback and context.
        
        Args:
            filename: File that caused error
            error: Exception object
            context: Optional context dictionary
        """
        error_type = type(error).__name__
        self.stats['errors_by_type'][error_type] += 1
        
        self.logger.error(f"\n{'-'*60}")
        self.logger.error(f"ERROR in {filename}: {error_type}")
        self.logger.error(f"{'-'*60}")
        self.logger.error(f"Message: {str(error)}")
        self.logger.error(f"\nTraceback:\n{traceback.format_exc()}")
        
        if context:
            self.logger.error(f"\nContext: {json.dumps(context, indent=2, default=str)}")
        
        self.logger.error(f"{'-'*60}\n")
    
    def log_validation_result(self, filename: str, validation_result: Dict[str, Any]):
        """
        Log validation results for a processed file.
        
        Args:
            filename: File name
            validation_result: Validation result dictionary
        """
        self.logger.debug(f"\nValidation for {filename}:")
        for key, value in validation_result.items():
            status = "✓" if value.get('passed') else "✗"
            self.logger.debug(f"  {status} {key}: {value.get('message', '')}")
    
    def generate_report(self):
        """
        Generate comprehensive migration report.
        
        Returns:
            Dict containing the report
        """
        self.stats['total'] = self.stats['success'] + self.stats['failed']
        success_rate = (self.stats['success'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': self.stats['total'],
                'successful': self.stats['success'],
                'failed': self.stats['failed'],
                'warnings': self.stats['warnings'],
                'success_rate': f"{success_rate:.2f}%"
            },
            'errors_by_type': dict(self.stats['errors_by_type']),
            'failed_files': self.stats['failed_files'],
            'edge_cases': self.stats['edge_cases'],
            'processing_statistics': {
                'total_files_processed': self.stats['total'],
                'average_processing_time': sum(self.stats['processing_times']) / len(self.stats['processing_times']) if self.stats['processing_times'] else 0
            },
            'log_files': {
                'debug_log': str(self.log_file),
                'error_log': str(self.error_file),
                'report_file': str(self.report_file)
            }
        }
        
        # Write report to JSON file
        with open(self.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Log summary
        self.logger.info(f"\n\n{'='*60}")
        self.logger.info("MIGRATION REPORT SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total files: {self.stats['total']}")
        self.logger.info(f"Successful: {self.stats['success']}")
        self.logger.info(f"Failed: {self.stats['failed']}")
        self.logger.info(f"Warnings: {self.stats['warnings']}")
        self.logger.info(f"Success rate: {success_rate:.2f}%")
        
        if self.stats['edge_cases']:
            self.logger.info(f"\nEdge cases found: {len(self.stats['edge_cases'])}")
            for case in self.stats['edge_cases'][:5]:  # Show first 5
                self.logger.info(f"  - {case['type']}: {case['file']}")
        
        if self.stats['errors_by_type']:
            self.logger.info(f"\nErrors by type:")
            for error_type, count in sorted(self.stats['errors_by_type'].items(), key=lambda x: x[1], reverse=True):
                self.logger.info(f"  - {error_type}: {count}")
        
        self.logger.info(f"\nReport saved to: {self.report_file}")
        self.logger.info(f"{'='*60}\n")
        
        return report
    
    def validate_json_output(self, json_file: str) -> Dict[str, Any]:
        """
        Validate JSON output format.
        
        Args:
            json_file: Path to JSON file to validate
        
        Returns:
            Validation result dictionary
        """
        result = {'passed': False, 'errors': [], 'warnings': []}
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Basic structure validation
            required_fields = ['doc_type', 'name', 'html']
            for field in required_fields:
                if field not in data:
                    result['errors'].append(f"Missing required field: {field}")
            
            # Content validation
            if data.get('html') and len(data['html']) < 10:
                result['warnings'].append("HTML content appears unusually short")
            
            if not result['errors']:
                result['passed'] = True
            
        except json.JSONDecodeError as e:
            result['errors'].append(f"Invalid JSON: {str(e)}")
        except FileNotFoundError:
            result['errors'].append(f"File not found: {json_file}")
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
        
        return result


def main():
    """Main entry point for debugging utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch migration debugging utility")
    parser.add_argument('--mode', choices=['debug', 'validate', 'report'], 
                       default='debug', help='Operation mode')
    parser.add_argument('--output-dir', default='migration_debug_logs',
                       help='Output directory for logs')
    parser.add_argument('--input-file', help='Input file to validate')
    
    args = parser.parse_args()
    
    debugger = MigrationDebugger(args.output_dir)
    
    if args.mode == 'validate' and args.input_file:
        result = debugger.validate_json_output(args.input_file)
        debugger.logger.info(f"Validation result: {json.dumps(result, indent=2)}")
    
    debugger.generate_report()


if __name__ == "__main__":
    main()
