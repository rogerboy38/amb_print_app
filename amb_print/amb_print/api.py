import frappe
from frappe import _


@frappe.whitelist()
def get_migration_status():
    """Get current migration status."""
    job_doc = frappe.get_single("Print Migration Job")
    return {
        "status": job_doc.status,
        "progress": job_doc.progress,
        "last_run": job_doc.last_run
    }


@frappe.whitelist()
def get_migration_logs(limit=50):
    """Get recent migration logs."""
    logs = frappe.get_all(
        "Print Migration Log",
        fields=["name", "document_type", "status", "error_message", "creation"],
        order_by="creation desc",
        limit=int(limit)
    )
    return logs


@frappe.whitelist()
def generate_pdf_for_document(doctype, docname, print_format=None):
    """Generate PDF for a specific document using Chromium backend."""
    from frappe.utils.pdf import get_pdf
    
    html = frappe.get_print(doctype, docname, print_format)
    pdf = get_pdf(html)
    
    return {
        "status": "success",
        "pdf_size": len(pdf)
    }


@frappe.whitelist()
def label_hello_world(sales_order):
    """Phase 11 skeleton: test label button wiring from Sales Order."""
    doc = frappe.get_doc("Sales Order", sales_order)
    items_list = ', '.join([row.item_code for row in doc.items[:5]])
    return f"Hello World from Sales Order {doc.name}\nCustomer: {doc.customer}\nFirst items: {items_list}"

@frappe.whitelist()
def print_label_pdf(doctype, docname, print_format, start_position=None, label_qty=None):
    """Generate and return PDF for label printing.

    Supports partial-sheet printing for Label Small 8 by allowing:
    - start_position: A1, B1, A2, B2, A3, B3, A4, B4
    - label_qty: number of labels to print starting from that slot
    """
    import base64
    import frappe
    from frappe.utils.pdf import get_pdf

    valid_positions = ["A1", "B1", "A2", "B2", "A3", "B3", "A4", "B4"]

    if start_position not in valid_positions:
        start_position = "A1"

    try:
        label_qty = int(label_qty or 1)
    except (TypeError, ValueError):
        label_qty = 1

    if label_qty < 1:
        label_qty = 1

    if label_qty > 8:
        label_qty = 8

    original_start_position = frappe.local.form_dict.get("start_position")
    original_label_qty = frappe.local.form_dict.get("label_qty")

    try:
        frappe.local.form_dict["start_position"] = start_position
        frappe.local.form_dict["label_qty"] = label_qty

        html = frappe.get_print(doctype, docname, print_format=print_format)
        pdf_content = get_pdf(html)

    finally:
        if original_start_position is None:
            frappe.local.form_dict.pop("start_position", None)
        else:
            frappe.local.form_dict["start_position"] = original_start_position

        if original_label_qty is None:
            frappe.local.form_dict.pop("label_qty", None)
        else:
            frappe.local.form_dict["label_qty"] = original_label_qty

    return {
        "doctype": doctype,
        "docname": docname,
        "print_format": print_format,
        "start_position": start_position,
        "label_qty": label_qty,
        "pdf_base64": base64.b64encode(pdf_content).decode("utf-8")
    }
