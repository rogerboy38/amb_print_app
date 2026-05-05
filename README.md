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

## 🖨️ Print Format Templates

The app includes ready-to-use print format templates:

| Print Format | DocType | Description |
|--------------|---------|-------------|
| PEDIDO_VENTAS_AMB | Sales Order | Professional sales order format with multi-section layout, dynamic page numbering |
| COTIZACION_AMB | Quotation | Modern quotation format with customer info, validity notice, signature areas |

### Installing Print Formats

After installing the app, import the print format fixtures:

```bash
bench --site your-site import-fixtures --app amb_print
```

### Customizing Templates

See the [WYSIWYG Print Format Guide](docs/WYSIWYG_PRINT_FORMAT_GUIDE.md) for detailed instructions on creating and modifying print formats.

### Documentation

- [WYSIWYG Print Format Guide](docs/WYSIWYG_PRINT_FORMAT_GUIDE.md) - Complete guide to print format development
- [Lessons Learned](docs/LESSONS_LEARNED.md) - Best practices from development experience
- [Project Roadmap](docs/PROJECT_ROADMAP.md) - Future development phases

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

## Independent PDF Generator (Playwright + Chromium)

As of `feat/independent-pdf-generator`, the label-printing path no longer goes
through `print_designer.pdf_generator.pdf.get_pdf` and never touches
wkhtmltopdf. The button **Print Recommended Format** on Batch AMB calls
`amb_print.amb_print.api.print_label_pdf`, which:

1. Reads the Print Format's `.html` template directly from disk (bypassing
   `frappe.get_print()`'s wrapper divs and 0.75in padding).
2. Renders to PDF via headless Chromium driven by
   [Playwright Python](https://playwright.dev/python/) — full @page CSS,
   flexbox, SVG, web fonts, all working.
3. Attaches the rendered PDF to the source doc as a public File (append).

### One-time install

```bash
# from your bench root, as the `frappe` user
cd ~/frappe-bench
./env/bin/pip install 'playwright>=1.50,<2.0'

# Install Chromium + system dependencies (run as root once for the deps,
# then as frappe for the binary download)
sudo ./env/bin/playwright install-deps chromium

# Persistent path inside the bench tree (recommended over ~/.cache)
export PLAYWRIGHT_BROWSERS_PATH=~/frappe-bench/playwright-browsers
./env/bin/playwright install chromium
```

Add to your shell profile (or to the bench's `gunicorn.conf.py` env section):

```bash
export PLAYWRIGHT_BROWSERS_PATH=~/frappe-bench/playwright-browsers
```

### Verify

```bash
cd ~/frappe-bench
./env/bin/python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    pg = b.new_page()
    pg.set_content('<h1>hello</h1>')
    print(f'OK — {len(pg.pdf(format=\"Letter\"))} bytes')
    b.close()
"
```

Then from a Frappe site:

```bash
bench --site sandbox.sysmayal.cloud execute amb_print.amb_print.api.ping
# expected: {"ok": True, "playwright_available": True, ...}
```

### Docker

See `docker/Containerfile.amb_print` and the
[INDEPENDENT_PDF_GENERATOR runbook](../docs/amb_print/INDEPENDENT_PDF_GENERATOR.md)
for image build instructions and `docker-compose.yml` overrides
(`shm_size: '1gb'`, `PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers`).

### Disabling the wkhtmltopdf fallback

If you want hard-fail behavior when Chromium is unreachable (decision #5
flipped):

```python
# in your site_config.json, or via frappe.flags at runtime
frappe.flags.amb_print_disable_wkhtml_fallback = True
```

…or set the env var `AMB_PRINT_DISABLE_WKHTML_FALLBACK=1`.
