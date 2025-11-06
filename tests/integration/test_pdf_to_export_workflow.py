"""Integration tests for PDF to export workflow.

Tests complete end-to-end workflows including:
- PDF mapping to export
- UI integration with exporters  
- Error handling across components
"""

import pytest
import os


@pytest.mark.integration
class TestPDFToExportWorkflow:
    """Tests for complete PDF to export workflow."""
    
    def test_full_workflow_pdf_to_html(self, sample_mapping_data, html_jinja_exporter_instance, temp_directory):
        """Test complete workflow: PDF mapping to HTML export."""
        # Setup
        output_path = os.path.join(temp_directory, "exported.html")
        
        # Execute
        result = html_jinja_exporter_instance.export(sample_mapping_data, output_path)
        
        # Verify
        assert result["status"] == "success"
        assert os.path.exists(output_path)
        with open(output_path, 'r') as f:
            content = f.read()
            assert len(content) > 0
    
    def test_workflow_with_validation(self, sample_mapping_data, base_exporter_instance, temp_directory):
        """Test workflow includes mandatory field validation."""
        # Setup
        result = base_exporter_instance.validate(sample_mapping_data)
        
        # Verify
        assert result["is_valid"] is True
    
    def test_workflow_rejects_invalid_data(self, invalid_mapping_no_product, html_jinja_exporter_instance, temp_directory):
        """Test workflow rejects invalid data early."""
        output_path = os.path.join(temp_directory, "rejected.html")
        result = html_jinja_exporter_instance.export(invalid_mapping_no_product, output_path)
        assert result["status"] != "success"


@pytest.mark.integration
class TestErrorHandlingWorkflow:
    """Tests for error handling across workflow."""
    
    def test_error_propagation(self, base_exporter_instance):
        """Test errors are collected and propagated."""
        base_exporter_instance.add_error("Workflow error")
        errors = base_exporter_instance.get_errors()
        assert len(errors) > 0
    
    def test_warning_tracking(self, base_exporter_instance):
        """Test warnings are tracked during workflow."""
        base_exporter_instance.add_warning("Workflow warning")
        warnings = base_exporter_instance.get_warnings()
        assert len(warnings) > 0
