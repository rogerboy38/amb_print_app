import frappe
FORMATS = ["Barrel Scan Sheet","Carta de Instrucciones Secado","Label 4 (Container)",
           "Shipping Label AMB","Shipping Label Box","Shipping Label 4up","Shipping Label 8up"]
def execute():
    # Frappe's standard PF sync does NOT overwrite `disabled` on pre-existing
    # records; force these app label formats button-only. Idempotent.
    for n in FORMATS:
        if frappe.db.exists("Print Format", n):
            frappe.db.set_value("Print Format", n, "disabled", 1)
