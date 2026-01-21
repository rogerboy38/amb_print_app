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
