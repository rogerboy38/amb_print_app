# AMB Print - Frappe App

**Print Format Migration Tool for ERPNext v16+ with Chromium PDF Backend**

A hybrid Frappe app that combines the original Python-based extraction pipeline with native Frappe integration for background jobs, scheduling, and UI management.

## 🎯 Overview

This project provides two modes of operation:

### Mode 1: Frappe App (Recommended)
- Background job processing via `frappe.enqueue`
- Chromium PDF engine integration (Frappe v16+)
- UI control panel for migration management
- Scheduled automation via Frappe scheduler
- Migration logs for monitoring and debugging

### Mode 2: Standalone CLI (Legacy)
- Direct Python script execution
- Manual batch processing
- Works outside Frappe environment

## 📋 Supported Documents

- **COA AMB** - Certificate of Analysis with inspection results
- **Quotation (Normal)** - Standard quotation format
- **Quotation (Escalated)** - Variant with escalation details

## Requirements

- Frappe v16.0.0+
- ERPNext v16.0.0+
- Python 3.14+

## 🚀 Installation (Frappe App)

```bash
# Clone the app
cd ~/frappe-bench
bench get-app https://github.com/rogerboy38/amb_print_app.git

# Install on your site
bench --site your-site install-app amb_print

# Run migrations
bench --site your-site migrate

# Restart for scheduler
bench restart
```

### Configuration

Add to your `site_config.json`:

```json
{
    "pdf_engine": "chromium",
    "amb_print": {
        "base_url": "https://your-site.frappe.cloud",
        "api_key": "your_api_key",
        "api_secret": "your_api_secret"
    }
}
```

## 📁 Project Structure

```
amb_print_app/
├── amb_print/                    # Frappe app module
│   ├── __init__.py
│   ├── hooks.py                 # Frappe hooks & scheduler
│   ├── modules.txt
│   ├── tasks.py                 # Background job definitions
│   ├── install.py               # Post-install hooks
│   ├── amb_print/               # Module directory
│   │   ├── api.py              # Whitelisted API methods
│   │   └── doctype/            # DocType definitions
│   │       ├── print_migration_job/
│   │       ├── print_migration_log/
│   │       └── print_migration_document_type/
│   └── core/                    # Core logic (original pipeline)
│       ├── batch_processor.py
│       └── erpnext_api.py
├── src/                         # Original standalone modules
│   ├── config.py
│   ├── pdf_parser.py
│   ├── template_generator.py
│   ├── exporters/
│   └── ui/
├── scripts/                     # Standalone CLI scripts
├── config/                      # Configuration files
├── pyproject.toml              # Frappe app metadata
└── README.md
```

## 🖥️ Usage (Frappe App)

1. Navigate to **Print Migration Job** in Frappe desk
2. Select document types to migrate
3. Click **Run Migration** button
4. Monitor progress in real-time
5. Check **Print Migration Log** for detailed results

### API Endpoints

```python
# Get migration status
frappe.call('amb_print.amb_print.api.get_migration_status')

# Get migration logs
frappe.call('amb_print.amb_print.api.get_migration_logs', limit=50)

# Generate PDF for a document
frappe.call('amb_print.amb_print.api.generate_pdf_for_document', 
    doctype='Sales Invoice', docname='INV-001')
```

## ⏰ Scheduler

Automated batch migration runs daily at 2 AM (configurable in `hooks.py`).

## 🔧 DocTypes

| DocType | Purpose |
|---------|---------|
| Print Migration Job | Control panel (Single DocType) |
| Print Migration Log | Audit trail for each migration |
| Print Migration Document Type | Link table for document selection |

## 🚀 Usage (Standalone CLI)

```bash
# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config/credentials.json.template config/credentials.json

# Run complete pipeline
python scripts/05_batch_migration.py
```

## 🔗 ERPNext Resources

- **Sandbox**: https://sysmayal.frappe.cloud
- **Production**: https://sysmayal.v.frappe.cloud

## 📄 License

MIT

---

**Version**: 1.0.0  
**Updated**: January 2026
