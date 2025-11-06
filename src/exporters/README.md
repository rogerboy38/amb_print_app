# Phase 2: Export Module - AMB Print Application

## Overview

Phase 2 implements the export functionality for converting mapped PDF fields into ERPNext-compatible formats. This module handles the transformation of user-mapped document layouts into production-ready print templates.

## Completed Components

### 1. **Module Structure** (`__init__.py`)
- Factory pattern for exporter instantiation
- `get_exporter(export_type)` function
- Supported types: `html`, `json`, `erpnext`

### 2. **Base Exporter Class** (`base_exporter.py`)
**Abstract base class defining exporter interface**

**Key Methods:**
- `export_mapping(mapping)` - Abstract method for export logic
- `validate_mapping(mapping)` - Abstract validation method
- `validate_mandatory_fields()` - Verify required fields
- `validate_child_table()` - Check table requirements
- `set_metadata()` - Add export metadata
- `get_export_info()` - Return status and errors

**Error Handling:**
- Error collection and reporting
- Warning system for non-critical issues
- Export status tracking

### 3. **HTML/Jinja2 Exporter** (`html_jinja_exporter.py`)
**Converts mapped fields to ERPNext-compatible Jinja2 HTML templates**

**Features:**
- Generates production-ready HTML/Jinja2 templates
- Field mapping to Jinja2 variables (`{{ doc.field }}`)
- Child table iteration support
- CSS styling for ERPNext compatibility
- HTML escaping and sanitization

**Output Format:**
```jinja2
{% set doc = doc %}
<!DOCTYPE html>
<html>
<head>
    <style>/* ERPNext print styles */</style>
</head>
<body>
    <div class="header">{{ doc.name }}</div>
    <div class="section">
        {% for field in fields %}
            <div><span class="label">{{ field }}</span>: {{ doc[field] }}</div>
        {% endfor %}
    </div>
    {% for row in doc.child_table %}
        <!-- Row content -->
    {% endfor %}
</body>
</html>
```

**Methods:**
- `export_mapping(mapping)` - Main export function
- `validate_mapping(mapping)` - Validation logic
- `_build_html_from_mapping()` - HTML generation
- `_build_table_html()` - Table structure generation
- `to_file(filepath)` - Write template to disk

## Remaining Components (Ready for Implementation)

### 4. **JSON Exporter** (`json_exporter.py`) - PLANNED
**Export mapping as structured JSON for API submission**

**Purpose:**
- Machine-readable format
- Direct ERPNext API compatibility
- Data validation schema

**Structure:**
```json
{
  "metadata": {"doctype": "COA AMB", "version": "1.0"},
  "fields": {...},
  "child_table": [...],
  "validation": {...}
}
```

### 5. **ERPNext API Exporter** (`erpnext_api_exporter.py`) - PLANNED
**Direct integration with ERPNext via Frappe API**

**Features:**
- Authenticate with ERPNext instance
- Submit print format directly
- Error handling for API failures
- Rollback on validation errors

**Methods:**
- `authenticate()` - ERPNext session auth
- `export_mapping()` - API submission
- `validate_on_server()` - Server-side validation
- `get_submission_status()` - Check submission result

## Usage Examples

### Using the Factory Pattern
```python
from src.exporters import get_exporter

# Get HTML exporter
exporter = get_exporter('html')
exporter.set_metadata('COA AMB', 'coa_amb_print_v1')

if exporter.validate_mapping(mapping_data):
    html_template = exporter.export_mapping(mapping_data)
    exporter.to_file('output/coa_amb.html')
else:
    errors = exporter.get_errors()
    print(f"Validation failed: {errors}")
```

### Direct Exporter Usage
```python
from src.exporters import HTMLJinjaExporter

exporter = HTMLJinjaExporter()
exporter.set_metadata(
    doctype='COA AMB',
    document_name='coa_amb_template',
    author='team'
)

jinja_template = exporter.export_mapping(mapped_fields)
print(exporter.get_export_info())
```

## Integration with UI

The exporters are called from the MappingEditorWindow when user clicks "Export to ERPNext":

```python
# In mapping_editor.py
self.export_btn.clicked.connect(self._handleExport)

def _handleExport(self):
    exporter = get_exporter('html')
    if exporter.export_mapping(self.current_mapping):
        # Save and submit
        self.exportRequested.emit(exporter.get_export_info())
```

## Validation Requirements

### Mandatory Fields (COA AMB)
- `product_item` - Required (Link field)
- `child_table` - Minimum 1 row

### Optional Fields
- All other fields in doctype
- Product information, approval dates, etc.

### Warnings (Non-blocking)
- Unmapped optional fields
- Missing field type information

## Dependencies

```
Jinja2>=3.0.0          # Template engine
requests>=2.28.0       # HTTP for API calls
frappe-client>=1.0.0   # ERPNext API client
```

## Error Handling Strategy

**Three-tier approach:**

1. **Validation Errors** - Block export
   - Missing mandatory fields
   - Invalid child table
   - Malformed mapping

2. **Warnings** - Log but allow
   - Missing optional fields
   - Unused mapped regions
   - Deprecated field types

3. **API Errors** - Retry logic
   - Connection failures
   - Authentication issues
   - Server validation errors

## Next Steps

### Immediate (Next Session)
- [ ] Implement JSON exporter
- [ ] Implement ERPNext API exporter
- [ ] Create integration tests
- [ ] Add retry logic for API calls

### Short Term
- [ ] Template preview functionality
- [ ] Batch export support
- [ ] Export history tracking
- [ ] Template versioning

### Medium Term
- [ ] AI-assisted field detection
- [ ] Custom exporter plugins
- [ ] Export performance optimization
- [ ] Multi-doctype support

## Testing

Test cases to implement:

```python
# test_base_exporter.py
def test_mandatory_field_validation()
def test_child_table_validation()
def test_error_collection()

# test_html_jinja_exporter.py
def test_html_generation()
def test_jinja_template_syntax()
def test_table_mapping()
def test_export_to_file()

# test_integration.py
def test_full_mapping_to_export_workflow()
def test_error_handling_workflow()
```

## Configuration

**Environment variables** (in `.env`):
```
ERPNEXT_URL=https://sysmayal.frappe.cloud
ERPNEXT_API_KEY=your_api_key
ERPNEXT_API_SECRET=your_api_secret
EXPORT_TIMEOUT=30  # seconds
RETRY_ATTEMPTS=3
```

## Performance Considerations

- Template caching for repeated exports
- Async API submissions for large batches
- Streaming for large HTML files
- Database connection pooling for API

---

**Status**: Phase 2 - 60% Complete
**Last Updated**: November 6, 2025
**Version**: 1.0-beta
