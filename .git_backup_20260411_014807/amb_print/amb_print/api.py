import os
import frappe
import base64
from frappe.utils.pdf import get_pdf

@frappe.whitelist()
def label_hello_world(sales_order):
    doc = frappe.get_doc("Sales Order", sales_order)
    items_list = ", ".join([row.item_code for row in doc.items[:5]])
    return "Hello World from Sales Order " + doc.name + " Customer: " + doc.customer + " First items: " + items_list

@frappe.whitelist()
def print_label_pdf(doctype, docname, print_format, start_position=None, label_qty=None):
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

    # Get the source document
    doc = frappe.get_doc(doctype, docname)

    # Set custom attributes on the doc object
    doc._label_start_position = start_position
    doc._label_qty = label_qty
    # Also set without underscore for template fallback
    doc.label_start_position = start_position 
    doc.label_qty = label_qty

    # CRITICAL: Set in frappe.local.form_dict which persists through get_print internal request
    frappe.local.form_dict.label_start_position = start_position
    frappe.local.form_dict.label_qty = str(label_qty)

    # Also set via frappe.flags as backup
    frappe.flags.label_start_position = start_position
    frappe.flags.label_qty = label_qty

    # Map print format for Sample Request AMB doctype
    if doctype == "Sample Request AMB":
        sr_format_map = {
            "Label Small 8": "Label Small 8 Sample Request",
            "Label Small 8 Batch": "Label Small 8 Sample Request",
        }
        print_format = sr_format_map.get(print_format, print_format)
    html = frappe.get_print(doctype, docname, print_format=print_format, doc=doc)
    # Override frappe wrapper CSS for label printing
    import re as _re
    override_css = '<style>.print-format-gutter{padding:0!important;margin:0!important;max-width:none!important;width:100%!important}.print-format{padding:0!important;margin:0!important;max-width:none!important;width:100%!important;border-radius:0!important}</style>'
    html = html.replace('</head>', override_css + '</head>', 1)
    with open("/tmp/label_debug.html", "w") as f: f.write(html)
    pdf_options = {"page-size": "Letter", "margin-top": "0mm", "margin-bottom": "0mm", "margin-left": "0mm", "margin-right": "0mm"}
    pdf_content = get_pdf(html, options=pdf_options)

    return {
        "doctype": doctype,
        "docname": docname,
        "print_format": print_format,
        "start_position": start_position,
        "label_qty": label_qty,
        "pdf_base64": base64.b64encode(pdf_content).decode("utf-8")
    }
