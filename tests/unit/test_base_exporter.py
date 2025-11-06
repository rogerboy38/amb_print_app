"""Unit tests for BaseExporter class.

Tests the core exporter functionality including:
- Mandatory field validation (Product Item)
- Child table validation (minimum 1 row)
- Error and warning collection
- Metadata tracking
"""

import pytest
from unittest.mock import Mock, patch


class TestBaseExporterValidation:
    """Tests for BaseExporter validation methods."""
    
    @pytest.mark.unit
    def test_mandatory_field_validation(self, base_exporter_instance, sample_mapping_data):
        """Test that Product Item field is validated as mandatory."""
        result = base_exporter_instance.validate_mandatory_fields(sample_mapping_data)
        assert result["is_valid"] is True
        assert "product_item" in result["validated_fields"]
    
    @pytest.mark.unit
    def test_mandatory_field_missing(self, base_exporter_instance, invalid_mapping_no_product):
        """Test validation fails when Product Item is missing."""
        result = base_exporter_instance.validate_mandatory_fields(invalid_mapping_no_product)
        assert result["is_valid"] is False
        assert "product_item" in result["errors"]
    
    @pytest.mark.unit
    def test_child_table_minimum_rows(self, base_exporter_instance, sample_mapping_data):
        """Test that child table has minimum 1 row."""
        result = base_exporter_instance.validate_child_table(sample_mapping_data)
        assert result["is_valid"] is True
        assert result["row_count"] >= 1
    
    @pytest.mark.unit
    def test_child_table_empty_invalid(self, base_exporter_instance, invalid_mapping_empty_table):
        """Test validation fails for empty child table."""
        result = base_exporter_instance.validate_child_table(invalid_mapping_empty_table)
        assert result["is_valid"] is False
        assert result["row_count"] == 0
    
    @pytest.mark.unit
    def test_error_collection(self, base_exporter_instance):
        """Test error collection mechanism."""
        base_exporter_instance.add_error("Test error")
        base_exporter_instance.add_error("Another error")
        errors = base_exporter_instance.get_errors()
        assert len(errors) == 2
        assert "Test error" in errors
    
    @pytest.mark.unit
    def test_warning_collection(self, base_exporter_instance):
        """Test warning collection mechanism."""
        base_exporter_instance.add_warning("Test warning")
        warnings = base_exporter_instance.get_warnings()
        assert len(warnings) == 1
        assert "Test warning" in warnings
    
    @pytest.mark.unit
    def test_metadata_tracking(self, base_exporter_instance, sample_mapping_data):
        """Test metadata is tracked during export."""
        base_exporter_instance.set_metadata("export_version", "1.0")
        base_exporter_instance.set_metadata("timestamp", "2024-01-01T00:00:00")
        metadata = base_exporter_instance.get_metadata()
        assert metadata["export_version"] == "1.0"
        assert metadata["timestamp"] == "2024-01-01T00:00:00"


class TestBaseExporterPipeline:
    """Tests for BaseExporter validation pipeline."""
    
    @pytest.mark.unit
    def test_validation_pipeline_success(self, base_exporter_instance, sample_mapping_data):
        """Test complete validation pipeline with valid data."""
        result = base_exporter_instance.validate(sample_mapping_data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
    
    @pytest.mark.unit
    def test_validation_pipeline_product_failure(self, base_exporter_instance, invalid_mapping_no_product):
        """Test validation pipeline detects missing product."""
        result = base_exporter_instance.validate(invalid_mapping_no_product)
        assert result["is_valid"] is False
        assert any("product" in str(err).lower() for err in result["errors"])
    
    @pytest.mark.unit
    def test_validation_pipeline_table_failure(self, base_exporter_instance, invalid_mapping_empty_table):
        """Test validation pipeline detects empty child table."""
        result = base_exporter_instance.validate(invalid_mapping_empty_table)
        assert result["is_valid"] is False
        assert any("table" in str(err).lower() for err in result["errors"])


class TestBaseExporterExport:
    """Tests for BaseExporter export functionality."""
    
    @pytest.mark.unit
    def test_export_method_exists(self, base_exporter_instance):
        """Test that export method is defined."""
        assert hasattr(base_exporter_instance, "export")
        assert callable(base_exporter_instance.export)
    
    @pytest.mark.unit
    def test_export_returns_result(self, base_exporter_instance, sample_mapping_data, temp_directory):
        """Test export returns proper result structure."""
        output_path = f"{temp_directory}/output.txt"
        result = base_exporter_instance.export(sample_mapping_data, output_path)
        assert "status" in result
        assert "data" in result


@pytest.mark.unit
class TestBaseExporterFactory:
    """Tests for exporter factory pattern."""
    
    def test_factory_returns_exporter(self, base_exporter_instance):
        """Test factory creates exporter instances."""
        assert base_exporter_instance is not None
        assert hasattr(base_exporter_instance, "export")
