"""
amb_print.amb_print.api
========================

Whitelisted public methods for the amb_print app. Thin facade — the heavy
lifting is in `amb_print.pdf` and `amb_print.label`.

History
-------
- v13.5.0 baseline (label_v11.0.0): three @whitelist methods including
  `print_label_pdf` calling `print_designer.pdf_generator.pdf.get_pdf`.
- v14.0.0 (this file): clean cut. `print_label_pdf` keeps the SAME
  signature and SAME return shape as v13.5.0 so existing JS clients
  (`batch_amb.js`) work unchanged, but renders via `amb_print.pdf.render_pdf`
  (Playwright) instead of going through `print_designer`. The legacy
  audit/diagnostic methods from earlier fix attempts are intentionally
  dropped — re-add them only if you actually still need them.

The "EXISTING METHODS GO HERE" block at the bottom is kept as a
placeholder for future @whitelist additions in v14.x — leave it empty
on the initial v14.0.0 commit.
"""

from __future__ import annotations

import base64
import logging

import frappe

logger = logging.getLogger(__name__)


# =============================================================================
# Public: print_label_pdf
# =============================================================================
# Signature MUST match v13.5.0 exactly — batch_amb.js calls this by name and
# expects pdf_base64 in the response.

@frappe.whitelist()
def print_label_pdf(doctype: str, docname: str, print_format: str,
                    save_attachment: int = 1, is_private: int = 0,
                    start_position=None, label_qty=None, sample_tags=None) -> dict:
    """Render a label PDF for (doctype, docname) using `print_format`.

    Parameters
    ----------
    doctype : str
        Source doctype, e.g. "Batch AMB".
    docname : str
        Source doc name, e.g. "LOTE-26-19-0001".
    print_format : str
        Print Format name, e.g. "Label Small 8 (Container)". Must be a
        Standard Jinja format on disk.
    save_attachment : int
        1 (default) attaches the PDF to the source doc as a public File;
        0 returns the PDF bytes only (base64 in `pdf_base64`).
    is_private : int
        0 (default) makes the attachment public; 1 makes it private.
    sample_tags : list[str] | str | None
        Track 5 (2026-09-02). 0-4 fixed phrases, e.g.
        ["MICROBIOLOGICAL ANALYSIS SAMPLE"]. Only honoured by
        "Label Small 8 (Container)"; other formats ignore it. Accepted as
        a JSON-encoded string too, since frappe.call serializes list args
        that way over HTTP.

    Returns
    -------
    dict
        {
            "doctype": <str>,
            "docname": <str>,
            "print_format": <str>,
            "pdf_size": <int bytes>,
            "file_url": <str|None>,    # None when save_attachment=0
            "file_name": <str|None>,
            "pdf_base64": <str>,       # always present
        }
    """
    from amb_print.amb_print.label import build_html, save_pdf_to_doc
    from amb_print.amb_print.pdf import render_pdf, LETTER_PORTRAIT_FULL_BLEED

    save_attachment = int(save_attachment)
    is_private = int(is_private)
    if isinstance(sample_tags, str):
        sample_tags = frappe.parse_json(sample_tags)

    logger.info("amb_print.print_label_pdf: %s %s via %s",
                doctype, docname, print_format)

    # 1) Build HTML directly from the print_format template (no Frappe wrapper)
    html = build_html(doctype=doctype, docname=docname,
                      print_format=print_format,
                      start_position=start_position, label_qty=label_qty,
                      sample_tags=sample_tags)

    # 2) Render to PDF via Playwright (Chromium). prefer_css_page_size=True
    #    means the template's @page rule wins, so labels go full bleed
    #    if their CSS says so.
    pdf_bytes = render_pdf(html, options=LETTER_PORTRAIT_FULL_BLEED)

    if not pdf_bytes:
        frappe.throw("amb_print: render produced empty PDF.",
                     title="amb_print: empty render")

    # 3) Optionally attach to the source doc (default behavior)
    file_url = None
    file_name = None
    if save_attachment:
        file_doc = save_pdf_to_doc(
            pdf_bytes=pdf_bytes,
            doctype=doctype,
            docname=docname,
            print_format=print_format,
            is_private=is_private,
        )
        file_url = file_doc.file_url
        file_name = file_doc.file_name

    return {
        "doctype": doctype,
        "docname": docname,
        "print_format": print_format,
        "pdf_size": len(pdf_bytes),
        "file_url": file_url,
        "file_name": file_name,
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }


# =============================================================================
# Public: ping (cheap health check for the new pipeline)
# =============================================================================

@frappe.whitelist()
def ping() -> dict:
    """Cheap health check: is the new pipeline wired up correctly?

    Returns engine availability so an operator can quickly verify a deploy
    without rendering a full label.
    """
    from amb_print.amb_print.pdf import playwright_engine, fallback

    return {
        "ok": True,
        "playwright_available": playwright_engine.is_available(),
        "wkhtmltopdf_available": fallback.is_available(),
        "browsers_path": playwright_engine.PLAYWRIGHT_BROWSERS_PATH,
    }


# =============================================================================
# Public: label_hello_world (Phase 11 skeleton — Sales Order)
# =============================================================================

@frappe.whitelist()
def label_hello_world(sales_order):
    """Phase 11 skeleton: test label button wiring from Sales Order."""
    doc = frappe.get_doc("Sales Order", sales_order)
    items_list = ', '.join([row.item_code for row in doc.items[:5]])
    return f"Hello World from Sales Order {doc.name}\nCustomer: {doc.customer}\nFirst items: {items_list}"


# =============================================================================
# FUTURE @whitelist METHODS GO BELOW
# =============================================================================
# v14.0.0 is a clean cut — `print_label_pdf`, `ping`, and `label_hello_world`
# are exposed. Add new @whitelist methods here as the v14.x line evolves
# (Sample Request AMB labels, BRL barrel labels, batch QR labels for warehouse
# pick lists, etc.) Keep them small — heavy lifting belongs in
# `amb_print.label.*` and `amb_print.pdf.*`, this file stays a thin facade.


@frappe.whitelist()
def print_document_pdf(doctype: str, docname: str, print_format: str,
                       save_attachment: int = 1, is_private: int = 0) -> dict:
    """Render a business DOCUMENT (proforma / memo) for (doctype, docname).

    Same pipeline as print_label_pdf (build_html -> Playwright -> attach), but
    letter-portrait WITH margins instead of full-bleed. Bypasses
    frappe.get_print() so it never hits the print wrapper / letterhead layer
    that 500s on Sample Request AMB.
    """
    from amb_print.amb_print.label import build_html, save_pdf_to_doc
    from amb_print.amb_print.pdf import render_pdf
    from amb_print.amb_print.pdf.options import PdfOptions

    save_attachment = int(save_attachment)
    is_private = int(is_private)

    logger.info("amb_print.print_document_pdf: %s %s via %s",
                doctype, docname, print_format)

    html = build_html(doctype=doctype, docname=docname, print_format=print_format)

    pdf_bytes = render_pdf(html, options=PdfOptions(
        page="Letter", margin_mm=12, prefer_css_page_size=False))

    if not pdf_bytes:
        frappe.throw("amb_print: render produced empty PDF.",
                     title="amb_print: empty render")

    file_url = None
    file_name = None
    if save_attachment:
        file_doc = save_pdf_to_doc(
            pdf_bytes=pdf_bytes, doctype=doctype, docname=docname,
            print_format=print_format, is_private=is_private)
        file_url = file_doc.file_url
        file_name = file_doc.file_name

    return {
        "doctype": doctype,
        "docname": docname,
        "print_format": print_format,
        "pdf_size": len(pdf_bytes),
        "file_url": file_url,
        "file_name": file_name,
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }
