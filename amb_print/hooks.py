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

# DocType JS - Load custom JS for specific DocTypes
doctype_js = {
    "Sales Order": "public/js/sales_order_labels.js",
    "Sample Request AMB": "public/js/sample_request_amb_labels.js"
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
        "dt": "Custom Field",
        "filters": [
            ["dt", "=", "Sample Request AMB"],
            ["fieldname", "in", ["section_labels_tab", "label_cells"]]
        ]
    }
]

# Scheduler Events
scheduler_events = {
    "cron": {
        "0 2 * * *": [
            "amb_print.tasks.scheduled_batch_migration"
        ]
    }
}

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
after_install = "amb_print.install.after_install"
