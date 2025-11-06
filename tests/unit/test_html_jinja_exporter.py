"""Unit tests for HTMLJinjaExporter class.

Tests the Jinja2 template export functionality including:
- HTML template generation
- Jinja2 syntax validation
- Table mapping to HTML
- File export functionality
"""

import pytest
import os
from unittest.mock import Mock, patch


class TestHTMLJinjaExporterGeneration:
    """Tests for HTMLJinjaExporter HTML generation."""
    
    @pytest.mark.unit
    def test_html_generation(self, html_jinja_exporter_instance, sample_mapping_data):
        """Test HTML is generated from mapping data."""
        html_content = html_jinja_exporter_instance.generate_html(sample_mapping_data)
        assert html_content is not None
        assert isinstance(html_content, str)
        assert len(html_content) > 0
    
    @pytest.mark.unit
    def test_html_contains_product_item(self, html_jinja_exporter_instance, sample_mapping_data):
        """Test generated HTML contains product item."""
        html_content = html_jinja_exporter_instance.generate_html(sample_mapping_data)
        assert "Product-001" in html_content
    
    @pytest.mark.unit
    def test_html_valid_structure(self, html_jinja_exporter_instance, sample_mapping_data):
        """Test generated HTML has valid structure."""
        html_content = html_jinja_exporter_instance.generate_html(sample_mapping_data)
        assert "<html" in html_content.lower() or "<!doctype" in html_content.lower()
        assert "</html>" in html_content.lower()


class TestHTMLJinjaExporterValidation:
    """Tests for HTMLJinjaExporter validation."""
    
    @pytest.mark.unit
    def test_jinja_syntax_valid(self, html_jinja_exporter_instance, sample_mapping_data):
        """Test Jinja2 template syntax is valid."""
        result = html_jinja_exporter_instance.validate_template_syntax(sample_mapping_data)
        assert result["is_valid"] is True
        assert "errors" not in result or len(result["errors"]) == 0
    
    @pytest.mark.unit
    def test_table_mapping_valid(self, html_jinja_exporter_instance, sample_mapping_data):
        """Test table data mapping is valid."""
        tables = html_jinja_exporter_instance.get_table_mappings(sample_mapping_data)
        assert tables is not None
        assert len(tables) > 0


class TestHTMLJinjaExporterExport:
    """Tests for HTMLJinjaExporter export functionality."""
    
    @pytest.mark.unit
    def test_export_to_file(self, html_jinja_exporter_instance, sample_mapping_data, temp_directory):
        """Test export writes HTML to file."""
        output_path = os.path.join(temp_directory, "output.html")
        result = html_jinja_exporter_instance.export(sample_mapping_data, output_path)
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert len(content) > 0
    
    @pytest.mark.unit
    def test_export_result_structure(self, html_jinja_exporter_instance, sample_mapping_data, temp_directory):
        """Test export returns proper result structure."""
        output_path = os.path.join(temp_directory, "output.html")
        result = html_jinja_exporter_instance.export(sample_mapping_data, output_path)
        assert "status" in result
        assert result["status"] == "success"
        assert "output_path" in result
    
    @pytest.mark.unit
    def test_export_validates_before_export(self, html_jinja_exporter_instance, invalid_mapping_no_product, temp_directory):
        """Test export validates data before processing."""
        output_path = os.path.join(temp_directory, "output.html")
        result = html_jinja_exporter_instance.export(invalid_mapping_no_product, output_path)
        assert result["status"] != "success"


class TestHTMLJinjaExporterIntegration:
    """Tests for HTMLJinjaExporter integration."""
    
    @pytest.mark.unit
    def test_export_complete_workflow(self, html_jinja_exporter_instance, sample_mapping_data, temp_directory):
        """Test complete export workflow."""
        output_path = os.path.join(temp_directory, "workflow.html")
        result = html_jinja_exporter_instance.export(sample_mapping_data, output_path)
        assert result["status"] == "success"
        assert os.path.exists(output_path)
