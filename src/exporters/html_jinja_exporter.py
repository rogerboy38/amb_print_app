
"""
HTML/Jinja Template Exporter for ERPNext Print Formats

Converts mapped PDF fields to ERPNext-compatible Jinja2 HTML templates
"""

from .base_exporter import BaseExporter
from typing import Dict, Any, List
import json
from jinja2 import Template, Environment


class HTMLJinjaExporter(BaseExporter):
    """
    Export mapped print format to HTML/Jinja2 template for ERPNext
    
    Generates:
    - Jinja2-based HTML template
    - Compatible with ERPNext Print Format
    - Supports child tables and dynamic fields
    """
    
    JINJA_TEMPLATE_SKELETON = """
{%- set doc = doc -%}
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { font-size: 18px; font-weight: bold; margin-bottom: 20px; }
        .section { margin-top: 15px; margin-bottom: 15px; }
        .field-label { font-weight: bold; display: inline-block; width: 150px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    {# Document Header #}
    <div class="header">{{ doc.name }}</div>
    
    {# Document Fields #}
    <div class="section">
        {{ content }}
    </div>
    
    {# Footer with metadata #}
    <div style="margin-top: 50px; font-size: 10px; color: #999;">
        <p>Generated on: {{ now() }}</p>
    </div>
</body>
</html>
    """
    
    def __init__(self):
        super().__init__()
        self.html_content = ""
        self.jinja_template = ""
    
    def export_mapping(self, mapping: Dict[str, Any]) -> str:
        """
        Export mapping to HTML/Jinja template
        
        Args:
            mapping (dict): Mapped fields from PDF
        
        Returns:
            str: Generated Jinja2 HTML template
        """
        if not self.validate_mapping(mapping):
            return ""
        
        self.mapping = mapping
        html_content = self._build_html_from_mapping(mapping)
        self.jinja_template = self._generate_jinja_template(html_content)
        
        return self.jinja_template
    
    def validate_mapping(self, mapping: Dict[str, Any]) -> bool:
        """
        Validate mapping for HTML export
        
        Args:
            mapping (dict): Mapping to validate
        
        Returns:
            bool: True if valid
        """
        self.clear_messages()
        
        # Validate mandatory fields
        required_fields = ['product_item']
        if not self.validate_mandatory_fields(mapping, required_fields):
            return False
        
        # Validate child table
        if not self.validate_child_table(mapping, 'child_table', min_rows=1):
            return False
        
        return True
    
    def _build_html_from_mapping(self, mapping: Dict[str, Any]) -> str:
        """
        Build HTML content from mapped fields
        
        Args:
            mapping (dict): Mapped fields
        
        Returns:
            str: HTML content
        """
        html_parts = []
        
        # Top-level fields
        html_parts.append("<div class=\"section\">")
        for field_name, field_value in mapping.items():
            if field_name != 'child_table' and isinstance(field_value, str):
                html_parts.append(
                    f'<div><span class=\"field-label\">{field_name}:</span> '
                    f'<span>{{{{ doc.{field_name} }}}}</span></div>'
                )
        html_parts.append("</div>")
        
        # Child table
        if 'child_table' in mapping and isinstance(mapping['child_table'], list):
            html_parts.append(self._build_table_html(mapping['child_table']))
        
        return "\n".join(html_parts)
    
    def _build_table_html(self, table_data: List[List[str]]) -> str:
        """
        Build HTML table from child table data
        
        Args:
            table_data (list): Table rows
        
        Returns:
            str: HTML table markup
        """
        if not table_data:
            return ""
        
        html_parts = [
            "<div class=\"section\"><b>Child Table</b>",
            "<table>",
            "<thead><tr>"
        ]
        
        # Table headers
        for i, col_name in enumerate([f"Column {i+1}" for i in range(len(table_data[0]))]):
            html_parts.append(f"<th>{col_name}</th>")
        html_parts.append("</tr></thead><tbody>")
        
        # Table body with Jinja iteration
        html_parts.append("{% for row in doc.child_table %}<tr>")
        for col_idx in range(len(table_data[0])):
            html_parts.append(f"<td>{{{{ row.field_{col_idx} }}}}</td>")
        html_parts.append("</tr>{% endfor %}</tbody></table></div>")
        
        return "\n".join(html_parts)
    
    def _generate_jinja_template(self, html_content: str) -> str:
        """
        Generate complete Jinja2 template
        
        Args:
            html_content (str): HTML content
        
        Returns:
            str: Complete Jinja2 template
        """
        return self.JINJA_TEMPLATE_SKELETON.replace("{{ content }}", html_content)
    
    def to_file(self, filepath: str) -> bool:
        """
        Write template to file
        
        Args:
            filepath (str): Output file path
        
        Returns:
            bool: Success status
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.jinja_template)
            return True
        except Exception as e:
            self.add_error(f"Failed to write template: {str(e)}")
            return False

    def generate_html(self, mapping: Dict[str, Any]) -> str:
        """
        Generate HTML content from mapping data
        
        Args:
            mapping (dict): Mapped fields from PDF
        
        Returns:
            str: Generated HTML content
        """
        if not isinstance(mapping, dict):
            self.add_error("Mapping must be a dictionary")
            return ""
        
        html_content = self._build_html_from_mapping(mapping)
        return html_content
    
    def validate_template_syntax(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Jinja2 template syntax
        
        Args:
            mapping (dict): Mapping data
        
        Returns:
            dict: Validation result with 'is_valid' and 'errors' keys
        """
        try:
            if not isinstance(mapping, dict):
                return {"is_valid": False, "errors": ["Mapping must be a dictionary"]}
            
            # Try to parse the template to check syntax
            html_content = self._build_html_from_mapping(mapping)
            template = Template(html_content)
            
            return {"is_valid": True, "errors": []}
        except Exception as e:
            return {"is_valid": False, "errors": [str(e)]}
    
    def get_table_mappings(self, mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract table mappings from mapping data
        
        Args:
            mapping (dict): Mapping data
        
        Returns:
            list: List of table mappings
        """
        tables = []
        
        if not isinstance(mapping, dict):
            return tables
        
        if 'child_table' in mapping and isinstance(mapping['child_table'], list):
            for idx, row in enumerate(mapping['child_table']):
                tables.append({
                    "table_index": idx,
                    "row_data": row if isinstance(row, dict) else {},
                    "columns": len(row) if isinstance(row, (list, dict)) else 0
                })
        
        return tables
    
    def export(self, mapping: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Export mapping to HTML file
        
        Args:
            mapping (dict): Mapping data to export
            output_path (str): Path where to save the HTML file
        
        Returns:
            dict: Export result with status and details
        """
        self.clear_messages()
        
        # Validate mapping first
        if not self.validate_mapping(mapping):
            return {
                "status": "error",
                "errors": self.get_errors(),
                "output_path": None
            }
        
        try:
            # Generate HTML content
            html_content = self.export_mapping(mapping)
            
            # Write to file
            success = self.to_file(output_path)
            
            if success:
                return {
                    "status": "success",
                    "output_path": output_path,
                    "errors": self.get_errors(),
                    "warnings": self.get_warnings()
                }
            else:
                return {
                    "status": "error",
                    "errors": self.get_errors(),
                    "output_path": None
                }
        except Exception as e:
            self.add_error(f"Export failed: {str(e)}")
            return {
                "status": "error",
                "errors": self.get_errors(),
                "output_path": None
            }
