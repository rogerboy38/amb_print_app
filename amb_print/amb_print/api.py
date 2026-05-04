import frappe
from frappe import _
from datetime import timedelta


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
def print_label_pdf(doctype, docname, print_format):
    """Generate and return PDF for label printing.
    
    BUG 93C fix: Use server-side method instead of direct API call to avoid whitelist issues.
    """
    from frappe.utils import sanitize_html
    from frappe.utils.pdf import get_pdf
    
    # Get the HTML for the document using the specified print format
    html = frappe.get_print(doctype, docname, print_format)
    
    # Generate PDF
    pdf_content = get_pdf(html)
    
    # Return as base64 encoded file for download
    import base64
    return {
        "doctype": "Sales Order",
        "docname": docname,
        "print_format": print_format,
        "pdf_base64": base64.b64encode(pdf_content).decode('utf-8')
    }


@frappe.whitelist()
def generate_label_cells(sr_name: str) -> dict:
    """
    Walk Sample Request AMB.samples and populate label_cells with one row
    per physical label cell. Existing label_cells rows are cleared first.

    Returns {"created": int, "skipped_overflow": int, "warning": str|None}
    """
    if not sr_name:
        frappe.throw(_("Sample Request name is required"))

    sr = frappe.get_doc("Sample Request AMB", sr_name)

    POSITIONS = ["A1", "B1", "A2", "B2", "A3", "B3", "A4", "B4"]
    TAG_PRIORITY = [
        ("for_microbiology",  "Microbiological Analysis Sample"),
        ("for_customer",      "Customer Retention Sample"),
        ("for_distributor",   "Distributor Retention Sample"),
        ("for_retention",     "AMB Wellness Retention"),
        ("for_external_lab",  "External Lab Sample"),
    ]

    md_date = sr.sample_sent_date or sr.request_date
    md_str = md_date.strftime("%d/%m/%y") if md_date else ""

    sr.set("label_cells", [])

    created = 0
    skipped_overflow = 0
    pos_idx = 0

    for s_idx, s in enumerate(sr.samples or [], start=1):
        item_name = ""
        shelf_life_days = 0
        weight_per_unit = None
        weight_uom = None
        if s.item:
            item_doc = frappe.db.get_value(
                "Item", s.item,
                ["item_name", "shelf_life_in_days", "weight_per_unit", "weight_uom"],
                as_dict=True,
            )
            if item_doc:
                item_name = item_doc.get("item_name") or ""
                shelf_life_days = int(item_doc.get("shelf_life_in_days") or 0)
                weight_per_unit = item_doc.get("weight_per_unit")
                weight_uom = item_doc.get("weight_uom")
        if not item_name:
            item_name = s.description or ""

        ed_str = ""
        if md_date and shelf_life_days:
            ed_date = md_date + timedelta(days=shelf_life_days)
            ed_str = ed_date.strftime("%d/%m/%y")

        if s.qty_per_sample and s.uom:
            net_weight = f"{s.qty_per_sample:g} {s.uom}"
        elif weight_per_unit and weight_uom:
            net_weight = f"{weight_per_unit:g} {weight_uom}"
        else:
            net_weight = ""

        sample_tag = ""
        for flag_name, tag_value in TAG_PRIORITY:
            if getattr(s, flag_name, 0):
                sample_tag = tag_value
                break

        count = max(1, int(s.samples_count or 1))
        for _i in range(count):
            if pos_idx >= len(POSITIONS):
                skipped_overflow += 1
                continue
            sr.append("label_cells", {
                "cell_position": POSITIONS[pos_idx],
                "parent_sample_idx": s_idx,
                "item_name": item_name,
                "lot": s.batch or "",
                "manufacture_date": md_str,
                "expiration_date": ed_str,
                "net_weight": net_weight,
                "sample_tag": sample_tag,
                "is_active": 1,
            })
            pos_idx += 1
            created += 1

    sr.save()
    frappe.db.commit()

    warning = None
    if skipped_overflow:
        warning = _("More than 8 cells would have been generated; only first 8 saved. {0} skipped.").format(skipped_overflow)

    return {"created": created, "skipped_overflow": skipped_overflow, "warning": warning}
