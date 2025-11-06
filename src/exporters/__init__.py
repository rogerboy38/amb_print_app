"""
Exporters Module - AMB Print Application
Convert mapped print format to ERPNext-compatible formats
"""

from .base_exporter import BaseExporter
from .html_jinja_exporter import HTMLJinjaExporter
from .json_exporter import JSONExporter
from .erpnext_api_exporter import ERPNextAPIExporter

__all__ = [
    'BaseExporter',
    'HTMLJinjaExporter',
    'JSONExporter',
    'ERPNextAPIExporter',
]

# Export factory
def get_exporter(export_type='html'):
    """
    Factory function to get appropriate exporter instance
    
    Args:
        export_type (str): 'html', 'json', or 'erpnext'
    
    Returns:
        Exporter instance
    """
    exporters = {
        'html': HTMLJinjaExporter,
        'json': JSONExporter,
        'erpnext': ERPNextAPIExporter,
    }
    
    if export_type not in exporters:
        raise ValueError(
            f"Unknown export type: {export_type}. "
            f"Supported: {', '.join(exporters.keys())}"
        )
    
    return exporters[export_type]()
