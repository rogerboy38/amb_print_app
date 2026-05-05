"""
amb_print.label.attach
======================

`save_pdf_to_doc(pdf_bytes, doctype, docname, print_format, is_private)`
inserts the rendered PDF as a Frappe `File` row in append mode (every render
produces a new attachment with a timestamped filename — never overwrites a
prior one).

Filename convention
-------------------
    <safe_format>-<safe_docname>-<YYYYMMDD_HHMMSS>.pdf

    e.g.  Label_Small_8_Container-LOTE-26-19-0001-20260504_154212.pdf

Slugification preserves dashes (LOTE-26-19-0001 stays readable) but replaces
parentheses, spaces, and other punctuation with underscores. Order matters:
format first, doc second, timestamp last — sorts naturally in the Attach
panel.
"""

from __future__ import annotations

import re
from datetime import datetime

import frappe


_SAFE_RE = re.compile(r"[^A-Za-z0-9_-]+")


def save_pdf_to_doc(pdf_bytes: bytes, doctype: str, docname: str,
                    print_format: str, is_private: int = 0):
    """Insert a File doc with the rendered PDF attached to (doctype, docname).

    Parameters
    ----------
    pdf_bytes : bytes
        Raw PDF content from `pdf.render_pdf`.
    doctype : str
        Source doctype (e.g. "Batch AMB").
    docname : str
        Source doc name (e.g. "LOTE-26-19-0001").
    print_format : str
        Used in the filename (e.g. "Label Small 8 (Container)").
    is_private : int
        0 (public, default) or 1 (private). Public files are accessible at
        their `file_url` without authentication; private files require a
        valid Frappe session.

    Returns
    -------
    frappe.model.document.Document
        The inserted File doc. Read `.file_url` and `.file_name`.
    """
    if not pdf_bytes:
        frappe.throw("amb_print: refusing to attach empty PDF bytes.",
                     title="amb_print: empty PDF")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_format = _SAFE_RE.sub("_", str(print_format)).strip("_")
    safe_docname = _SAFE_RE.sub("_", str(docname)).strip("_")
    file_name = f"{safe_format}-{safe_docname}-{ts}.pdf"

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "is_private": int(is_private),
        "content": pdf_bytes,
    })
    file_doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return file_doc
