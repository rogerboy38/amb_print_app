"""
Base Exporter Class for AMB Print Application

Abstract base class defining interface for all exporters
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
from datetime import datetime


class BaseExporter(ABC):
    """
    Abstract base class for export implementations
    
    All exporters must implement:
    - export_mapping(): Convert mapping to target format
    - validate_mapping(): Check mapping validity
    """
    
    def __init__(self):
        self.mapping = {}
        self.metadata = {}
        self.errors = []
        self.warnings = []
    
    @abstractmethod
    def export_mapping(self, mapping: Dict[str, Any]) -> Any:
        """
        Export mapped fields to target format
        
        Args:
            mapping (dict): Field mapping from PDF to ERPNext
        
        Returns:
            Exported format (HTML, JSON, etc.)
        """
        pass
    
    @abstractmethod
    def validate_mapping(self, mapping: Dict[str, Any]) -> bool:
        """
        Validate mapping before export
        
        Args:
            mapping (dict): Mapping to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    def set_metadata(self, doctype: str, document_name: str, **kwargs):
        """
        Set metadata for export (ERPNext doctype, document name, etc.)
        
        Args:
            doctype (str): ERPNext doctype name
            document_name (str): Document/template name
            **kwargs: Additional metadata
        """
        self.metadata = {
            'doctype': doctype,
            'document_name': document_name,
            'export_time': datetime.now().isoformat(),
            **kwargs
        }
    
    def add_error(self, error: str):
        """Add export error message"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add export warning message"""
        self.warnings.append(warning)
    
    def get_errors(self) -> List[str]:
        """Get list of errors"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """Get list of warnings"""
        return self.warnings
    
    def clear_messages(self):
        """Clear error and warning messages"""
        self.errors = []
        self.warnings = []
    
    def validate_mandatory_fields(self, mapping: Dict, required_fields: List[str]) -> bool:
        """
        Validate that all required fields are in mapping
        
        Args:
            mapping (dict): Field mapping
            required_fields (list): List of mandatory field names
        
        Returns:
            bool: True if all required fields present
        """
        for field in required_fields:
            if field not in mapping or not mapping[field]:
                self.add_error(f"Mandatory field '{field}' not mapped")
                return False
        return True
    
    def validate_child_table(self, mapping: Dict, table_field: str, min_rows: int = 1) -> bool:
        """
        Validate child table requirements
        
        Args:
            mapping (dict): Field mapping
            table_field (str): Name of child table field
            min_rows (int): Minimum required rows
        
        Returns:
            bool: True if valid
        """
        if table_field not in mapping:
            self.add_error(f"Child table '{table_field}' not found in mapping")
            return False
        
        table_data = mapping[table_field]
        if not isinstance(table_data, list) or len(table_data) < min_rows:
            self.add_error(
                f"Child table '{table_field}' requires "
                f"at least {min_rows} row(s), found {len(table_data) if isinstance(table_data, list) else 0}"
            )
            return False
        
        return True
    
    def get_export_info(self) -> Dict[str, Any]:
        """
        Get export information and status
        
        Returns:
            dict: Status, errors, warnings, metadata
        """
        return {
            'success': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'timestamp': datetime.now().isoformat(),
        }
