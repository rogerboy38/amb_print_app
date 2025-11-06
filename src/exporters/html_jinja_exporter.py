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
