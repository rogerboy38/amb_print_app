import frappe


def after_install():
    """Setup after app installation."""
    frappe.msgprint("Print Migration Tool installed successfully!")
