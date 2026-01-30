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

# DocTypes
fixtures = [
    {
        "doctype": "Print Format",
        "filters": {
            "module": "AMB Print"
        }
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
