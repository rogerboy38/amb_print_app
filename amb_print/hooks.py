app_name = "amb_print"
app_title = "Print Migration Tool"
app_publisher = "Sysmayal"
app_description = "Migrate legacy PDF formats to ERPNext Print Designer with Chromium PDF backend"
app_version = "1.0.0"
app_icon = "octicon octicon-file-pdf"
app_color = "#e74c3c"
app_email = "admin@sysmayal.com"
app_license = "MIT"

# Required apps
required_apps = ["frappe", "erpnext"]

# DocType JS - Load custom JS for specific DocTypes.
# NOTE: "Sample Request AMB" is a CUSTOM doctype (custom=1). frappe's FormMeta.add_code()
# bails on `if self.custom: return`, so doctype_js (and the doctype's own module .js) is
# silently ignored for it. Its "Shipping Label" button is therefore shipped as a Client Script
# fixture (see fixtures below + fixtures/client_script.json), which add_custom_script DOES apply
# to custom doctypes. Batch AMB / Sales Order are standard doctypes, so doctype_js works there.
doctype_js = {
    "Sales Order": "public/js/sales_order_labels.js",
    "Batch AMB": "public/js/batch_amb_labels.js"
}

# DocTypes
fixtures = [
    {
        "doctype": "Print Format",
        "filters": {
            "module": "AMB Print"
        }
    },
    {
        "doctype": "Client Script",
        "filters": {
            "module": "AMB Print"
        }
    }
]

# Scheduler Events
# RETIRED 2026-08-03: the nightly `0 2 * * *` cron ran
# amb_print.tasks.scheduled_batch_migration, which rendered up to 100 documents per
# configured doctype through Chromium every night and DISCARDED every PDF
# (_process_single_document returned it; the caller dropped the return value, and
# ERPNextAPI.upload_file was never called anywhere in core/). Replaced by an on-demand
# single-document run: amb_print.tasks.migrate_single_document, button on Print
# Migration Job.
#
# NOTE: removing this hook does NOT retire the existing `Scheduled Job Type` row —
# that row keeps firing until it is stopped. The companion patch
# amb_print.amb_print.patches.v16_retire_nightly.retire_scheduled_batch_migration
# sets stopped=1 so both halves travel together in one change.

# Background job queues
queues = {
    "print_migration": {
        "timeout": 3600,
        "background_workers": 2
    }
}

# Jinja Environment
jenv = {
    "methods": [],
    "filters": []
}

# Installation
# Independent PDF Generator: install Chromium binary on app install
after_install = "amb_print.amb_print.install.after_install"
