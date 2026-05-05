"""
amb_print.label.render
======================

`build_html(doctype, docname, print_format)` reads a Print Format's `.html`
template directly from disk, renders it with Frappe's Jinja environment,
and wraps it in a minimal `<!DOCTYPE html><html>…` envelope.

This bypasses `frappe.get_print()` entirely, which is the whole point: that
function wraps our HTML in:

    <div class="print-format-gutter">
      <div class="print-format" style="max-width: 8.3in; padding: 0.75in">
        ...our template...
      </div>
    </div>

The 0.75in padding and 8.3in max-width are exactly what produced the white
gutter on labels. Even with `!important` overrides we lose to the
@page-rule that print_designer's `add_page_size_css` injects via CDP after
load. The clean fix is to never produce that wrapper in the first place.

What this module does NOT do
----------------------------
- Apply letterhead / signature / cover-page logic. Labels never want those.
- Honor Print Format Style. Labels carry their own CSS in the .html file.
- Insert a print-format div. We control 100% of the HTML reaching Chromium.
"""

from __future__ import annotations

import os
from html import escape as _html_escape
from typing import Any

import frappe
from frappe.modules import get_module_path

# Slug resolution: use frappe.scrub (top-level, modern Frappe) so we match
# the slug Frappe itself uses on disk. Critically, frappe.scrub PRESERVES
# parens — "Label Small 8 (Container)" -> "label_small_8_(container)" — so
# the on-disk folder must include them too. The older `from frappe.utils
# import scrub` path doesn't exist in v15+; using the top-level frappe.scrub
# avoids a silent fallback to a regex that strips parens (which produced the
# wrong slug `label_small_8_container` and caused TemplateNotFoundError).
def _scrub(s: str) -> str:
    try:
        return frappe.scrub(s)
    except AttributeError:
        # Last-resort fallback for very old Frappe versions only.
        from frappe.utils import scrub as _legacy_scrub  # type: ignore
        return _legacy_scrub(s)


def build_html(doctype: str, docname: str, print_format: str) -> str:
    """Render the print_format's .html template directly to a complete HTML doc.

    Parameters
    ----------
    doctype : str
        e.g. "Batch AMB"
    docname : str
        e.g. "LOTE-26-19-0001"
    print_format : str
        e.g. "Label Small 8 (Container)"

    Returns
    -------
    str
        A complete HTML document ready to feed to `pdf.render_pdf`.

    Raises
    ------
    frappe.ValidationError
        If the print format is not a Standard Jinja format on disk, or if
        the template file is missing.
    """
    pf = frappe.get_doc("Print Format", print_format)

    if not (pf.print_format_type == "Jinja"
            and pf.standard == "Yes"
            and pf.module):
        frappe.throw(
            f"Print format {print_format!r} is not a Standard Jinja format "
            "on disk. amb_print's label pipeline only supports git-tracked "
            "templates — convert the Print Format to Standard or use a "
            "different printing path.",
            title="amb_print: unsupported print format",
        )

    module_path = get_module_path(pf.module)
    slug = _scrub(pf.name)
    template_path = os.path.join(
        module_path, "print_format", slug, slug + ".html"
    )

    if os.path.exists(template_path):
        with open(template_path, encoding="utf-8") as fh:
            tpl_src = fh.read()
    elif pf.html:
        # Fallback: standard=Yes formats whose .html file isn't on disk yet
        # (or DB-authored formats with html stored on the DocType row).
        # This matches Frappe's own browser-preview behavior — Frappe reads
        # from pf.html when the disk file is absent.
        tpl_src = pf.html
    else:
        frappe.throw(
            f"Template not found at {template_path} AND Print Format "
            f"{print_format!r} has no html field on its DocType row. "
            "Either commit the .html file under print_format/<slug>/ "
            "(slug is `frappe.scrub(name)` — parens are preserved!), or "
            "edit the Print Format in the desk and save the body field.",
            title="amb_print: template missing",
        )

    doc_obj = frappe.get_doc(doctype, docname)

    # Jinja context — keep it minimal and predictable. Templates that need
    # additional context can call frappe.get_doc / frappe.db.get_value
    # directly inside Jinja.
    context: dict[str, Any] = {
        "doc": doc_obj,
        "frappe": frappe,
    }
    inner = frappe.render_template(tpl_src, context)

    return _wrap(inner, title=f"{doctype} {docname}")


def _wrap(inner_html: str, title: str = "") -> str:
    """Wrap rendered template in a minimal HTML5 envelope.

    The <style> block resets html/body margins/padding to zero and forces
    backgrounds (colors and images) to print exactly as authored. Without
    `print-color-adjust: exact`, Chromium drops background fills on print
    — which produces apparently-empty white labels.

    No print-format wrapper, no max-width, no page padding. The template
    is responsible for its own page geometry (typically a `@page` rule
    with the right paper size and zero margins).
    """
    safe_title = _html_escape(title)
    return (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{safe_title}</title>\n"
        "<style>\n"
        "  html, body { margin: 0; padding: 0; }\n"
        "  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }\n"
        "</style>\n"
        "</head>\n"
        f"<body>\n{inner_html}\n</body>\n"
        "</html>\n"
    )
