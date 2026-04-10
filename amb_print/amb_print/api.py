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
    doc = frappe.get_doc(doctype, docname)
    doc._label_start_position = start_position
    doc._label_qty = label_qty
    html = frappe.get_print(doctype, docname, print_format=print_format, doc=doc)
    pdf_content = get_pdf(html)
    return {
        "doctype": doctype,
        "docname": docname,
        "print_format": print_format,
        "start_position": start_position,
        "label_qty": label_qty,
        "pdf_base64": base64.b64encode(pdf_content).decode("utf-8")
    }
