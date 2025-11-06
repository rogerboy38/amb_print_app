# Phase 3: Test Suite & Quality Assurance

## Overview

Phase 3 implements comprehensive testing infrastructure for the AMB Print Application, ensuring reliability, maintainability, and production readiness.

## Test Framework Setup

### Configuration Files
- **pytest.ini** - Main pytest configuration
  - Test discovery patterns (test_*.py)
  - Coverage requirements (80% minimum)
  - Test markers for categorization
  - Logging and reporting options
  - Timeout and asyncio settings

## Test Suite Structure

```
tests/
├── __init__.py                          # Test package marker
├── conftest.py                          # Pytest fixtures and configuration
├── fixtures/                            # Test data and utilities
│   ├── __init__.py
│   ├── sample_mappings.py              # Sample PDF→ERPNext mappings
│   ├── sample_pdfs/                    # Test PDF files
│   └── mock_data.py                    # Mock ERPNext data
├── unit/                               # Unit tests for components
│   ├── __init__.py
│   ├── test_base_exporter.py           # Base exporter tests
│   ├── test_html_jinja_exporter.py     # HTML exporter tests
│   ├── test_pdf_preview.py             # PDF widget tests
│   ├── test_field_palette.py           # Field widget tests
│   ├── test_table_mapper.py            # Table widget tests
│   └── test_signature_uploader.py      # Signature upload tests
├── integration/                         # End-to-end workflow tests
│   ├── __init__.py
│   ├── test_mapping_to_export.py       # Full workflow
│   ├── test_ui_to_export.py            # UI → Export flow
│   └── test_erpnext_integration.py     # ERPNext API tests
└── performance/                         # Performance and load tests
    ├── __init__.py
    └── test_export_performance.py      # Export speed benchmarks
```

## Unit Tests Strategy

### Base Exporter Tests
```python
# test_base_exporter.py
def test_mandatory_field_validation():
    """Verify Product Item field is enforced"""
    exporter = BaseExporter()
    mapping = {}  # Missing product_item
    assert not exporter.validate_mandatory_fields(mapping, ['product_item'])
    assert len(exporter.get_errors()) > 0

def test_child_table_validation():
    """Verify minimum 1 row requirement"""
    exporter = BaseExporter()
    mapping = {'child_table': []}  # Empty table
    assert not exporter.validate_child_table(mapping, 'child_table', min_rows=1)

def test_error_collection():
    """Verify error tracking system"""
    exporter = BaseExporter()
    exporter.add_error("Test error")
    exporter.add_warning("Test warning")
    assert len(exporter.get_errors()) == 1
    assert len(exporter.get_warnings()) == 1
```

### HTML/Jinja2 Exporter Tests
```python
# test_html_jinja_exporter.py
def test_html_generation():
    """Verify HTML template generation"""
    exporter = HTMLJinjaExporter()
    mapping = {
        'product_item': 'Item-001',
        'child_table': [['param1', 'value1', 'unit1', 'pass', 'note1']]
    }
    template = exporter.export_mapping(mapping)
    assert '{% for row in doc.child_table %}' in template
    assert '{{ doc.product_item }}' in template

def test_jinja_syntax_validation():
    """Verify generated Jinja2 syntax is valid"""
    exporter = HTMLJinjaExporter()
    mapping = {...}
    template = exporter.export_mapping(mapping)
    # Attempt to compile template - will raise error if invalid
    from jinja2 import Environment
    env = Environment()
    env.from_string(template)  # Should not raise

def test_table_mapping():
    """Verify child table HTML generation"""
    exporter = HTMLJinjaExporter()
    mapping = {
        'product_item': 'Item',
        'child_table': [['row1'], ['row2']]
    }
    template = exporter.export_mapping(mapping)
    assert template.count('{% for row') >= 1

def test_export_to_file(tmp_path):
    """Verify template file output"""
    exporter = HTMLJinjaExporter()
    exporter.jinja_template = '<html></html>'
    output_file = tmp_path / "test.html"
    assert exporter.to_file(str(output_file))
    assert output_file.read_text() == '<html></html>'
```

### UI Component Tests
```python
# test_pdf_preview.py
def test_pdf_preview_initialization():
    """Verify PDF preview widget creation"""
    from src.ui import PDFPreviewWidget
    widget = PDFPreviewWidget()
    assert widget.pdf_doc is None
    assert widget.current_page == 0

def test_pdf_page_navigation():
    """Verify page navigation works"""
    widget = PDFPreviewWidget(pdf_path='sample.pdf')
    initial_page = widget.current_page
    widget.nextPage()
    assert widget.current_page == initial_page + 1

# test_field_palette.py
def test_field_palette_search():
    """Verify field search filtering"""
    from src.ui import FieldPaletteWidget
    schema = {
        'fields': [
            {'name': 'product_item', 'label': 'Item', 'mandatory': True},
            {'name': 'approval_date', 'label': 'Date', 'mandatory': False}
        ]
    }
    widget = FieldPaletteWidget(schema)
    widget.search_input.setText('product')
    # Verify filtering logic

# test_table_mapper.py
def test_table_mapper_minimum_rows():
    """Verify 1 minimum row enforcement"""
    from src.ui import TableMapperWidget
    widget = TableMapperWidget()
    assert widget.table_widget.rowCount() >= 1
    widget._removeRow()  # Should fail or warn
    assert widget.table_widget.rowCount() >= 1
```

## Integration Tests Strategy

```python
# test_mapping_to_export.py
def test_full_workflow():
    """Test complete PDF→Export→File workflow"""
    # 1. Load sample PDF
    pdf_path = 'tests/fixtures/sample_pdfs/coa_amb.pdf'
    
    # 2. Create mapping
    mapping = {
        'product_item': 'Item-123',
        'child_table': [['param1', 'value1', 'unit1', 'pass', 'note1']]
    }
    
    # 3. Export to HTML
    from src.exporters import get_exporter
    exporter = get_exporter('html')
    template = exporter.export_mapping(mapping)
    
    # 4. Verify output
    assert template is not None
    assert len(exporter.get_errors()) == 0
    assert 'Item-123' in template or '{{ doc' in template

def test_ui_to_export_flow():
    """Test UI component integration"""
    # 1. Create mapping editor
    from src.ui import MappingEditorWindow
    editor = MappingEditorWindow()
    
    # 2. Populate with data
    editor.current_mapping = {...}
    
    # 3. Trigger export
    # (Mock signal emission)
    assert editor._validateMapping()
```

## Performance Tests Strategy

```python
# test_export_performance.py
def test_export_speed():
    """Benchmark export time for large mappings"""
    import time
    from src.exporters import get_exporter
    
    # Create large mapping (100+ fields, 50+ table rows)
    large_mapping = create_large_mapping()
    
    exporter = get_exporter('html')
    start = time.time()
    template = exporter.export_mapping(large_mapping)
    elapsed = time.time() - start
    
    assert elapsed < 1.0  # Should complete within 1 second
```

## Test Execution

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Category
```bash
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests
pytest -m "not requires_erpnext"  # Exclude ERPNext tests
```

### Generate Coverage Report
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run with Markers
```bash
pytest -m "unit and not slow"   # Fast unit tests
pytest -m "integration"         # Integration only
```

## CI/CD Integration

### GitHub Actions Workflow (.github/workflows/tests.yml)
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Test Data & Fixtures

### conftest.py
```python
import pytest

@pytest.fixture
def sample_mapping():
    """Provide sample COA AMB mapping"""
    return {
        'product_item': 'Item-001',
        'product_name': 'Test Product',
        'child_table': [
            ['Parameter 1', 'Value 1', 'Unit 1', 'Pass', 'Note 1'],
            ['Parameter 2', 'Value 2', 'Unit 2', 'Pass', 'Note 2']
        ]
    }

@pytest.fixture
def erpnext_mock():
    """Mock ERPNext API responses"""
    # Mock authentication and API calls
    pass
```

## Coverage Goals

- **Overall**: ≥ 80%
- **Exporters**: ≥ 90%
- **UI Components**: ≥ 75%
- **Integration**: ≥ 85%

## Success Criteria

✅ All unit tests passing
✅ Coverage ≥ 80%
✅ No critical bugs found in integration tests
✅ Performance tests show < 1s export time
✅ CI/CD pipeline automated

## Next Steps

1. Create fixture files and sample data
2. Implement unit test suite
3. Implement integration tests
4. Setup CI/CD workflows
5. Achieve 80% coverage
6. Document test results

---

**Status**: Phase 3 - Planning & Setup (25% Complete)
**Last Updated**: November 6, 2025
**Version**: 1.0-beta
