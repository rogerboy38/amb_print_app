"""
Template Generator Module

Converts extracted PDF elements into ERPNext print format templates.
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from loguru import logger

from jinja2 import Template, Environment, FileSystemLoader

from pdf_parser import PDFElement


class TemplateGenerator:
    """Generates ERPNext print format templates from PDF elements."""
    
    def __init__(self, output_format: str = "html"):
        """Initialize template generator."""
        self.output_format = output_format  # 'html' or 'json'
        self.elements: List[PDFElement] = []
        self.template_data = {}
        
        logger.info(f"Template generator initialized with format: {output_format}")
    
    def set_elements(self, elements: List[PDFElement]) -> None:
        """Set PDF elements for template generation."""
        self.elements = elements
        logger.info(f"Set {len(elements)} elements for template generation")
    
    def generate_html_template(self) -> str:
        """Generate ERPNext HTML Jinja2 template."""
        html_template = """
{% extends "print_format.html" %}

{% block style %}
<style>
    .print-format {{
        font-family: Arial, sans-serif;
        font-size: 12px;
        line-height: 1.5;
    }}
    .section {{
        margin-bottom: 20px;
        page-break-inside: avoid;
    }}
    .title {{
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    .field-label {{
        font-weight: bold;
        display: inline-block;
        width: 150px;
    }}
    .field-value {{
        display: inline-block;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }}
    th, td {{
        border: 1px solid #ccc;
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #f5f5f5;
        font-weight: bold;
    }}
</style>
{% endblock %}

{% block content %}
<div class="print-format">
    <div class="section">
        <div class="title">{{ doc.name }}</div>
    </div>
    
    {% for element in elements %}
    {% if element.type == 'text' %}
    <div class="field">
        <span class="field-label">{{ element.content }}:</span>
        <span class="field-value">{{ doc.get(element.content, '') }}</span>
    </div>
    {% endif %}
    {% endfor %}
</div>
{% endblock %}
        """
        
        return html_template
    
    def generate_json_template(self) -> str:
        """Generate ERPNext JSON template."""
        template_data = {
            "doc_type": "Print Format",
            "name": "Custom Print Format",
            "print_format_type": "Jinja",
            "fields": [
                {
                    "fieldname": element.content,
                    "label": element.content,
                    "fieldtype": "Data",
                    "idx": idx
                }
                for idx, element in enumerate(self.elements, 1)
                if element.element_type == "text"
            ]
        }
        
        return json.dumps(template_data, indent=2)
    
    def generate(self) -> str:
        """Generate template based on configured output format."""
        if not self.elements:
            logger.warning("No elements set for template generation")
            return ""
        
        if self.output_format == "json":
            template = self.generate_json_template()
        else:  # default to HTML
            template = self.generate_html_template()
        
        logger.info(f"Generated template in {self.output_format} format")
        return template
    
    def save_to_file(self, output_path: str) -> None:
        """Save generated template to file."""
        template = self.generate()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write(template)
        
        logger.info(f"Template saved to: {output_path}")
    
    def render_template(self, context: Dict[str, Any] = None) -> str:
        """Render template with given context data."""
        if context is None:
            context = {}
        
        template_str = self.generate_html_template()
        template = Template(template_str)
        
        rendered = template.render(
            elements=self.elements,
            **context
        )
        
        return rendered
    
    def export_for_erpnext(self, output_path: str, format_type: str = "html") -> str:
        """Export template in ERPNext-compatible format."""
        self.output_format = format_type
        template = self.generate()
        self.save_to_file(output_path)
        
        logger.info(f"Exported template to {output_path} in {format_type} format")
        return template
