"""Pytest configuration and fixtures for AMB Print Application tests.

Provides reusable fixtures for:
- Sample mapping data (COA AMB doctype with mandatory fields)
- PDF test files
- Mock ERPNext data
- Temporary file/directory management
- Mock HTTP responses for API tests
"""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest
from datetime import datetime
from typing import Dict, Any


# ===== MAPPING DATA FIXTURES =====

@pytest.fixture
def sample_mapping_data():
    """Sample COA AMB mapping with all required fields."""
    return {
        "doctype": "COA AMB",
        "name": "AMB-COA-001",
        "product_item": "Product-001",  # MANDATORY FIELD
        "mapping_version": "1.0",
        "created_date": datetime.now().isoformat(),
        "field_mappings": [
            {"field_name": "item_code", "page": 1, "x": 10, "y": 20, "mapped": True},
            {"field_name": "description", "page": 1, "x": 10, "y": 40, "mapped": True},
        ],
        "child_table_data": [
            {"row_number": 1, "column_headers": ["Item", "Qty", "Rate"], "data": ["ITEM-001", "10", "100"]}
        ],
    }


@pytest.fixture
def invalid_mapping_no_product():
    """Mapping without mandatory Product Item field."""
    return {
        "doctype": "COA AMB",
        "name": "AMB-COA-002",
        "product_item": None,  # INVALID - MANDATORY FIELD MISSING
        "field_mappings": [],
    }


@pytest.fixture
def invalid_mapping_empty_table():
    """Mapping with empty child table (violates minimum 1 row requirement)."""
    return {
        "doctype": "COA AMB",
        "name": "AMB-COA-003",
        "product_item": "Product-001",
        "child_table_data": [],  # INVALID - REQUIRES MINIMUM 1 ROW
    }


# ===== FILE AND PATH FIXTURES =====

@pytest.fixture
def temp_directory():
    """Create and cleanup temporary directory for tests."""
    temp_dir = tempfile.mkdtemp(prefix="amb_test_")
    yield temp_dir
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_pdf_path(temp_directory):
    """Create a sample PDF file path for testing."""
    pdf_path = os.path.join(temp_directory, "sample.pdf")
    # Create a minimal PDF
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n")
    return pdf_path


@pytest.fixture
def sample_image_file(temp_directory):
    """Create a sample image file for signature upload testing."""
    image_path = os.path.join(temp_directory, "signature.png")
    # Create minimal PNG file
    with open(image_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
    return image_path


# ===== MOCK ERPNEXT FIXTURES =====

@pytest.fixture
def mock_erpnext_client():
    """Mock ERPNext API client."""
    client = MagicMock()
    client.get_list.return_value = [
        {"name": "Product-001", "item_name": "Test Product"},
        {"name": "Product-002", "item_name": "Test Product 2"},
    ]
    client.get.return_value = {"name": "COA-001", "doctype": "COA AMB"}
    return client


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for API testing."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": {"name": "COA-001"}}
    return response


# ===== EXPORTER FIXTURES =====

@pytest.fixture
def 135
():
    """Base exporter instance for testing."""
    from src.exporters.base_exporter import BaseExporter
    
class TestExporter(BaseExporter):
        """Test exporter implementing all abstract methods."""
        
        def export_mapping(self, mapping: Dict[str, Any]) -> Any:
            """Implement abstract export_mapping method."""
            return {"status": "success", "data": mapping}
        
        def validate_mapping(self, mapping: Dict[str, Any]) -> bool:
            """Implement abstract validate_mapping method."""
            return True
        
        def export(self, mapping_data, output_path):
            """Export data to file."""
            return {"status": "success", "data": mapping_data}
@pytest.fixture
def html_jinja_exporter_instance():
    """HTML/Jinja2 exporter instance for testing."""
    from src.exporters.html_jinja_exporter import HTMLJinjaExporter
    return HTMLJinjaExporter()


# ===== UI COMPONENT FIXTURES =====

@pytest.fixture
def qt_app():
    """Create QApplication instance for Qt tests."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_pdf_viewer():
    """Mock PDF viewer widget for testing."""
    viewer = MagicMock()
    viewer.load_pdf.return_value = True
    viewer.get_current_page.return_value = 1
    viewer.get_total_pages.return_value = 3
    return viewer


# ===== PERFORMANCE TEST FIXTURES =====

@pytest.fixture
def large_mapping_data():
    """Generate large mapping data for performance testing."""
    mappings = []
    for i in range(100):
        mappings.append({
            "field_name": f"field_{i}",
            "page": (i % 10) + 1,
            "x": i * 10,
            "y": i * 5,
            "mapped": True
        })
    
    return {
        "doctype": "COA AMB",
        "name": "PERF-TEST-001",
        "product_item": "Product-001",
        "field_mappings": mappings,
        "child_table_data": [
            {"row_number": i, "data": [f"item_{i}", str(i * 10)]} 
            for i in range(50)
        ],
    }


# ===== INTEGRATION TEST FIXTURES =====

@pytest.fixture
def integration_test_environment(temp_directory, mock_erpnext_client):
    """Full integration test environment with all components."""
    return {
        "temp_dir": temp_directory,
        "erpnext_client": mock_erpnext_client,
        "test_mapping": {
            "doctype": "COA AMB",
            "name": "INT-TEST-001",
            "product_item": "Product-001",
            "field_mappings": [],
            "child_table_data": [{"row_number": 1, "data": []}],
        },
    }


# ===== PYTEST CONFIGURATION =====

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as a UI component test"
    )
