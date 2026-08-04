"""amb_print.amb_print.label.context

Source-agnostic label/document context resolver (T-label-rebuild Phase 1).

`get_label_context(doctype, docname)` returns a NORMALIZED dict that label and
shipping-document print formats read, so one template works regardless of the
source DocType (Sample Request AMB, Sales Order, Quotation, Opportunity, Lead,
Batch AMB). Registered as a Jinja method in hooks.py:

    jinja = {"methods": ["amb_print.amb_print.label.context.get_label_context"]}

Then in a print format:

    {% set ctx = get_label_context(doc.doctype, doc.name) %}

The function runs as trusted server-side Python (NOT safe_exec), so it may use
frappe.get_doc / frappe.db freely. Every field read is defensive (.get) so a
missing field on any source DocType yields None rather than raising.
"""

import frappe

# Default exporter/manufacturer (shown on shipping labels). Kept here rather than
# hardcoded in templates; can be promoted to a Single/Settings later.
DEFAULT_EXPORTER = "AGROMAYAL BOTANICA S.A. DE C.V."


def _first(doc, *names):
    """Return the first non-empty field value among `names`."""
    for n in names:
        v = doc.get(n)
        if v not in (None, ""):
            return v
    return None


def _resolve_source(doc):
    """Resolution order for a Sample Request AMB's source document:
    future Dynamic Link (related_to_type/related_to_doc, Phase 2) ->
    Sales Order -> Quotation -> Lead/Opportunity (via party_type/party).
    Returns (doctype, name) or (None, None)."""
    rt, rn = doc.get("related_to_type"), doc.get("related_to_doc")
    if rt and rn:
        return rt, rn
    if doc.get("sales_order_related"):
        return "Sales Order", doc.get("sales_order_related")
    if doc.get("quotation"):
        return "Quotation", doc.get("quotation")
    if doc.get("party_type") in ("Lead", "Opportunity") and doc.get("party"):
        return doc.get("party_type"), doc.get("party")
    return None, None


def _load_barrels_from_batch(ctx, batch_doc):
    """Append one normalized barrel dict per Container Barrels child row."""
    if not ctx.get("golden_number"):
        ctx["golden_number"] = _first(batch_doc, "golden_number", "custom_golden_number")
    if not ctx.get("product"):
        ctx["product"] = _first(batch_doc, "item_name", "item_to_manufacture")
    for r in (batch_doc.get("container_barrels") or []):
        ctx["barrels"].append({
            "serial": r.get("barrel_serial_number"),
            "net_weight": r.get("net_weight"),
            "gross_weight": r.get("gross_weight"),
            "tara_weight": r.get("tara_weight"),
            "item_name": r.get("label_item_name"),
            "lot": r.get("label_lot"),
            "mfg_date": r.get("label_manufacture_date"),
            "exp_date": r.get("label_expiration_date"),
            "active": r.get("label_is_active"),
        })


def get_label_context(doctype, docname):
    """Return a normalized label/document context dict for any source DocType."""
    doc = frappe.get_doc(doctype, docname)

    ctx = {
        "source_doctype": doctype,
        "source_name": docname,
        "exporter": DEFAULT_EXPORTER,
        "customer": None,
        "customer_name": None,
        "consignee": None,
        "product": None,
        "lot": None,
        "golden_number": None,
        "po": None,
        "mfg_date": None,
        "exp_date": None,
        "control_number": None,
        "is_export": False,
        "sub_product": None,
        "dest_plant": None,
        "language": "en",
        "related_doctype": None,
        "related_name": None,
        "contact_person": None,
        "address": None,
        "barrels": [],
        "items": [],
    }

    # Language: Sample Request uses letter_language; COA-style uses coa_language.
    if doc.get("letter_language") == "Carta Español" or doc.get("coa_language") == "Spanish":
        ctx["language"] = "es"

    if doctype == "Sample Request AMB":
        ctx["customer"] = doc.get("customer")
        ctx["customer_name"] = _first(doc, "customer_name") or doc.get("customer")
        ctx["consignee"] = _first(doc, "customer_name", "customer")
        ctx["product"] = _first(doc, "item_name", "wo_item_name", "item")
        ctx["golden_number"] = doc.get("custom_golden_number")
        ctx["po"] = _first(doc, "customer_po", "po_number")
        ctx["contact_person"] = doc.get("contact_person")
        ctx["address"] = doc.get("address")
        ctx["related_doctype"], ctx["related_name"] = _resolve_source(doc)
        batch = doc.get("batch_reference")
        if batch and frappe.db.exists("Batch AMB", batch):
            ctx["lot"] = batch
            bdoc = frappe.get_doc("Batch AMB", batch)
            _load_barrels_from_batch(ctx, bdoc)
            # SR-1 (a): M.D./E.D. derived from the batch; blank-clean when batch unset.
            ctx["mfg_date"] = _first(bdoc, "manufacturing_date", "production_end_date")
            ctx["exp_date"] = bdoc.get("expiry_date")
        for r in (doc.get("samples") or []):
            ctx["items"].append({
                "item": _first(r, "item_code", "item"),
                "item_name": r.get("item_name") or r.get("description"),
                "qty": r.get("total_qty") or r.get("samples_count") or r.get("qty"),
                "control_number": r.get("control_number"),
            })

    elif doctype == "Sales Order":
        ctx["customer"] = doc.get("customer")
        ctx["customer_name"] = _first(doc, "customer_name") or doc.get("customer")
        ctx["consignee"] = _first(doc, "customer_name", "customer")
        ctx["po"] = doc.get("po_no")
        for r in (doc.get("items") or []):
            ctx["items"].append({
                "item": r.get("item_code"),
                "item_name": r.get("item_name"),
                "qty": r.get("qty"),
            })
        if ctx["items"]:
            ctx["product"] = ctx["items"][0]["item_name"] or ctx["items"][0]["item"]

    elif doctype == "Batch AMB":
        ctx["lot"] = docname
        _load_barrels_from_batch(ctx, doc)
        ctx["sub_product"] = _first(doc, "custom_subfamily", "custom_product_family")
        ctx["dest_plant"] = _first(doc, "target_plant", "current_plant2", "manufacturing_plant")
        # Hybrid export detection: SO via work order, else a linked Sample Request.
        so_name = None
        wo = doc.get("work_order_ref")
        if wo and frappe.db.exists("Work Order", wo):
            so_name = frappe.db.get_value("Work Order", wo, "sales_order")
        sr = None
        if not so_name:
            _srl = frappe.get_all(
                "Sample Request AMB",
                filters={"batch_reference": docname},
                fields=["name", "sales_order_related", "quotation",
                        "related_to_type", "related_to_doc", "customer",
                        "customer_name", "contact_person", "address",
                        "letter_language"],
                order_by="modified desc", limit=1,
            )
            sr = _srl[0] if _srl else None
            if sr:
                so_name = sr.get("sales_order_related")
        if so_name and frappe.db.exists("Sales Order", so_name):
            so = frappe.get_doc("Sales Order", so_name)
            ctx["customer"] = so.get("customer")
            ctx["customer_name"] = so.get("customer_name") or so.get("customer")
            ctx["consignee"] = so.get("customer_name") or so.get("customer")
            ctx["po"] = so.get("po_no")
            ctx["contact_person"] = so.get("contact_person")
            ctx["related_doctype"] = "Sales Order"
            ctx["related_name"] = so_name
            ctx["is_export"] = True
        elif sr:
            rel_dt = sr.get("related_to_type")
            rel_dn = sr.get("related_to_doc")
            party = sr.get("customer_name") or sr.get("customer")
            if not party and rel_dt and rel_dn and frappe.db.exists(rel_dt, rel_dn):
                _rd = frappe.get_doc(rel_dt, rel_dn)
                party = _first(_rd, "customer_name", "company_name",
                               "party_name", "lead_name", "title")
            if party:
                ctx["customer_name"] = party
                ctx["consignee"] = party
                ctx["contact_person"] = sr.get("contact_person")
                ctx["related_doctype"] = rel_dt or "Sample Request AMB"
                ctx["related_name"] = rel_dn or sr.get("name")
                ctx["is_export"] = True
            _ll = sr.get("letter_language") or ""
            if _ll.startswith("Carta Esp"):
                ctx["language"] = "es"

    elif doctype in ("Quotation", "Opportunity", "Lead"):
        ctx["customer"] = _first(doc, "party_name", "customer")
        ctx["customer_name"] = _first(
            doc, "customer_name", "company_name", "party_name", "lead_name", "title"
        )
        ctx["consignee"] = ctx["customer_name"]

    # Fallback control number = golden number if not otherwise set.
    if not ctx["control_number"]:
        ctx["control_number"] = ctx.get("golden_number")

    return ctx


def set_label_fields(doc, method=None, print_settings=None):
    """before_print hook (F-SR1-A): resolve the label context server-side and stash
    the consignee on the in-memory doc, so label print formats read
    ``doc.label_consignee`` instead of calling ``frappe.get_attr`` in Jinja (which the
    Frappe 16 safe-exec sandbox blocks). Scoped to the doc being printed — the print
    path already enforces read permission on it (printview.validate_print_permission),
    so this adds no data-read surface. Best-effort: never break a print."""
    try:
        ctx = get_label_context(doc.doctype, doc.name)
        doc.label_consignee = ctx.get("consignee")
        # SR-1 D1: lote de venta = the COA-authoritative golden the resolver already
        # sources one-hop from the linked COA (SR.coa_amb) / the batch golden.
        doc.label_lote_de_venta = ctx.get("golden_number")
        # Box/shipping labels use the full context dict; expose it so they read
        # doc.label_ctx.* instead of calling the resolver via frappe.get_attr.
        doc.label_ctx = ctx
    except Exception:
        frappe.log_error(frappe.get_traceback(), "amb_print set_label_fields")
