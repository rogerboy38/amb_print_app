# AMB Print Application - Test Suite Documentation

## Overview

This directory contains the comprehensive test suite for the ERPNext Print Designer Migration Tool. The test suite includes:

- **Unit Tests**: Individual component testing (fixtures, exporters, UI components)
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Benchmarking and performance validation
- **CI/CD Automation**: GitHub Actions workflows for continuous testing

## Directory Structure

```
tests/
├── __init__.py                           # Tests package initialization
├── conftest.py                          # Pytest configuration and fixtures
├── README.md                            # This file
├── unit/                                # Unit tests
│   ├── __init__.py
│   ├── test_base_exporter.py           # BaseExporter validation tests
│   └── test_html_jinja_exporter.py     # HTMLJinjaExporter tests
└── integration/                         # Integration tests
    ├── __init__.py
    └── test_pdf_to_export_workflow.py  # End-to-end workflow tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Run Integration Tests Only
```bash
pytest tests/integration/ -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run with Markers
```bash
pytest tests/ -m unit -v
pytest tests/ -m integration -v
```

## Fixtures

All fixtures are defined in `conftest.py`. Key fixtures include:

### Mapping Data
- `sample_mapping_data`: Valid COA AMB mapping with all required fields
- `invalid_mapping_no_product`: Invalid mapping missing Product Item
- `invalid_mapping_empty_table`: Invalid mapping with empty child table

### File Management
- `temp_directory`: Temporary directory for test files
- `sample_pdf_path`: Sample PDF file
- `sample_image_file`: Sample image for signature upload

### Mock Objects
- `mock_erpnext_client`: Mock ERPNext API client
- `mock_http_response`: Mock HTTP response
- `base_exporter_instance`: BaseExporter instance
- `html_jinja_exporter_instance`: HTMLJinjaExporter instance

## Test Categories

### Unit Tests

**test_base_exporter.py**
- Mandatory field validation (Product Item)
- Child table validation (minimum 1 row)
- Error and warning collection
- Metadata tracking
- Complete validation pipeline
- Export functionality

**test_html_jinja_exporter.py**
- HTML generation from mapping data
- Jinja2 syntax validation
- Table data mapping
- File export functionality
- Complete workflow testing

### Integration Tests

**test_pdf_to_export_workflow.py**
- Complete PDF to HTML export workflow
- Validation during workflow execution
- Error handling across components
- Warning tracking

## Coverage Goals

- **Overall**: ≥ 80% (enforced by pytest configuration)
- **Exporters**: ≥ 90% coverage
- **UI Components**: ≥ 75% coverage
- **Integration**: ≥ 85% coverage

## CI/CD Integration

GitHub Actions workflow (`.github/workflows/tests.yml`) automatically:

1. Runs on every push to `master` and `develop` branches
2. Tests against Python 3.9, 3.10, and 3.11
3. Generates coverage reports
4. Enforces 80% minimum coverage
5. Uploads results to codecov
6. Performs linting checks

## Key Testing Principles

### Mandatory Field Validation
All exports validate:
- Product Item field is mandatory
- Child table must have minimum 1 row

### Error Handling
Tests ensure:
- Errors are collected and reported
- Warnings are tracked
- Invalid data is rejected early

### Data Integrity
Tests verify:
- Mapping data is preserved during export
- File paths are correct
- Output files are created successfully

## Development Workflow

### Adding New Tests

1. Create test file in `tests/unit/` or `tests/integration/`
2. Use `@pytest.mark.unit` or `@pytest.mark.integration` decorator
3. Use fixtures from `conftest.py`
4. Follow naming convention: `test_*.py`
5. Run tests before committing

### Example Test

```python
@pytest.mark.unit
class TestMyComponent:
    def test_basic_functionality(self, sample_mapping_data):
        # Arrange
        expected = "result"
        
        # Act
        result = my_function(sample_mapping_data)
        
        # Assert
        assert result == expected
```

## Performance Considerations

Tests are designed to:
- Run quickly (< 5 seconds total for CI)
- Use temporary directories (no cleanup issues)
- Mock external dependencies
- Focus on component behavior

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `PYTHONPATH` includes project root
2. **Fixture not found**: Check `conftest.py` spelling
3. **Coverage below 80%**: Add tests for uncovered lines
4. **Permission errors**: Ensure temp directories are writable

## Success Criteria

✅ All tests pass on CI/CD pipeline  
✅ Coverage ≥ 80%  
✅ No linting errors  
✅ Integration tests validate end-to-end workflows  
