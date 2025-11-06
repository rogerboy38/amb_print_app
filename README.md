# ERPNext Print Designer Migration Tool

**Hybrid Automation Workflow for PDF → ERPNext Print Format Migration**

A complete Python-based extraction and automation pipeline for migrating legacy PDF report designs to ERPNext print formats using AI-assisted templating and direct API integration.

## 🎯 Project Overview

This project automates the migration of three key print format documents:
- **COA AMB** - Certificate of Analysis with inspection results
- **Quotation (Normal)** - Standard quotation format
- **Quotation (Escalated)** - Variant with escalation details

## 📋 Features

✅ **PDF Extraction** - Generate PDFs directly from ERPNext sandbox using REST API
✅ **Structure Parsing** - Extract tables, text, and layout from PDFs using pdfplumber
✅ **Field Mapping** - Automatic mapping of PDF fields to ERPNext DocType fields
✅ **Batch Processing** - Process multiple documents with error handling and retry logic
✅ **API Integration** - Direct upload of print formats to ERPNext via REST API
✅ **Comprehensive Logging** - Track all operations and errors
✅ **Multi-Environment** - Support for TestProd and Production environments

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone git@github.com:rogerboy38/amb_print_app.git
cd amb_print_app

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config/credentials.json.template config/credentials.json
# Edit config/credentials.json with your ERPNext API keys
```

### Usage

```bash
# Option 1: Run complete pipeline
python scripts/05_batch_migration.py

# Option 2: Run individual steps
python scripts/01_extract_pdfs.py           # Generate PDFs
python scripts/02_parse_structures.py       # Extract structures
python scripts/03_generate_mappings.py      # Create mappings
python scripts/04_upload_formats.py         # Upload to ERPNext
```

## 📁 Project Structure

```
amb_print_app/
├── src/                          # Core Python modules
│   ├── erpnext_api.py           # ERPNext API client
│   ├── pdf_extractor.py         # PDF parsing engine
│   ├── field_mapper.py          # Field mapping schemas
│   ├── batch_processor.py       # Batch processing logic
│   └── utils.py                 # Utility functions
├── scripts/                     # Executable scripts
│   ├── 01_extract_pdfs.py      # PDF generation
│   ├── 02_parse_structures.py  # Structure extraction
│   ├── 03_generate_mappings.py # Mapping generation
│   ├── 04_upload_formats.py    # API uploads
│   └── 05_batch_migration.py   # Complete pipeline
├── config/                      # Configuration files
│   ├── credentials.json.template
│   └── environments.json
├── data/                        # Data directories
│   ├── extracted_pdfs/         # Generated PDFs
│   ├── pdf_structures/         # JSON structures
│   └── field_mappings/         # Mapping schemas
├── logs/                        # Log files
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Configuration

Edit `config/credentials.json` with your ERPNext credentials:

```json
{
  "environments": {
    "testprod": {
      "url": "https://sysmayal.frappe.cloud",
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET"
    },
    "production": {
      "url": "https://sysmayal.v.frappe.cloud",
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET"
    }
  }
}
```

## 📊 Workflow Phases

### Phase 1: PDF Extraction & Field Mapping
- Generates PDFs from ERPNext sandbox
- Extracts table structures, text, and layout
- Creates JSON field mapping schemas
- **Status**: ✅ Implemented

### Phase 2: Template Refinement
- Review generated PDFs
- Refine templates via ERPNext Print Designer UI
- Validate field mappings
- **Status**: ℹ️ Manual in ERPNext

### Phase 3: Quotation Variants
- Create Quotation Normal print format
- Create Quotation Escalated variant
- Apply conditional styling/sections
- **Status**: ✅ Mapping prepared

### Phase 4: API Automation & Testing
- Automated batch processing
- API validation and error handling
- Sandbox → Production migration
- **Status**: ✅ Implemented

## 📝 API Credentials (TestProd)

Credentials are pre-configured for:
- **Base URL**: `https://sysmayal.frappe.cloud`
- **API Key**: `1ae51d15c7633b7`
- **API Secret**: `cf2f4056efb7b1d`

## 📚 Documentation

- **Extract PDFs**: See `scripts/01_extract_pdfs.py`
- **Parse Structures**: See `scripts/02_parse_structures.py`
- **Field Mappings**: See `src/field_mapper.py`
- **API Integration**: See `src/erpnext_api.py`
- **Batch Processing**: See `src/batch_processor.py`

## 🔗 ERPNext Resources

- **Sandbox**: https://sysmayal.frappe.cloud
- **Production**: https://sysmayal.v.frappe.cloud

## 📄 License

MIT

---

**Created**: November 2025
**Version**: 1.0.0
