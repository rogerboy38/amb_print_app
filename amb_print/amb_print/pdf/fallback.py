"""
amb_print.pdf.fallback
======================

Last-resort renderer for amb_print when Playwright + Chromium aren't
available — for example, a freshly-built Docker image where
`playwright install chromium` hasn't run yet, or a sandbox where the
Chromium binary got cleaned up by a system update.

This path is **discouraged** for label printing because:
    - wkhtmltopdf's WebKit fork (Qt 5.x circa 2015) has broken flexbox
    - It cannot render Code 128 SVG barcodes consistently
    - It is officially abandonware (last release 2020)

But hard-failing the whole "Print Recommended Format" button when
Chromium is briefly unavailable is worse than producing a wonky-but-
non-empty PDF that the operator can re-render later. Hence this exists.

If decision #5 in the project plan is ever flipped to "hard-fail
without Chromium", delete this file and remove the import from
`pdf/__init__.py`.
"""

from __future__ import annotations

import logging
import shutil
from typing import Optional

from .options import PdfOptions, from_kwargs

logger = logging.getLogger(__name__)


def render_pdf_wkhtml(html: str, options: Optional[PdfOptions] = None,
                      **option_overrides) -> bytes:
    """Render HTML to PDF via wkhtmltopdf (last resort).

    Translates our PdfOptions to wkhtmltopdf-style hyphen keys and calls
    Frappe's `get_pdf`. We deliberately do NOT route through
    `print_designer.pdf_generator.pdf.get_pdf` — that wraps HTML in
    print-format-gutter divs and re-injects @page rules, which is exactly
    what we're trying to escape.

    Returns
    -------
    bytes
        PDF content from wkhtmltopdf.

    Raises
    ------
    RuntimeError
        If wkhtmltopdf binary is not found on PATH.
    Exception
        Anything Frappe's wrapper raises, surfaced unmodified.
    """
    if shutil.which("wkhtmltopdf") is None:
        raise RuntimeError(
            "wkhtmltopdf binary not found on PATH; cannot fall back. "
            "Install Chromium for Playwright (preferred) or install "
            "wkhtmltopdf system-wide."
        )

    if options is None:
        options = from_kwargs(**option_overrides)
    elif option_overrides:
        merged = {f: getattr(options, f) for f in options.__dataclass_fields__}
        merged.update(option_overrides)
        options = from_kwargs(**merged)

    wk_options = _to_wkhtmltopdf_options(options)

    # Frappe's frappe.utils.pdf.get_pdf calls wkhtmltopdf via pdfkit. It
    # accepts hyphenated wkhtmltopdf-style keys directly.
    from frappe.utils.pdf import get_pdf

    logger.warning("amb_print: rendering via wkhtmltopdf fallback "
                   "(label fidelity will be reduced)")
    return get_pdf(html, options=wk_options)


def _to_wkhtmltopdf_options(opts: PdfOptions) -> dict:
    """Map our dataclass to wkhtmltopdf's CLI-style flags."""
    wk: dict = {
        "print-media-type": True,
        "no-outline": True,
        "encoding": "UTF-8",
        "disable-smart-shrinking": True,  # critical: we want exact pixel sizes
    }

    # Page size
    if isinstance(opts.page, str):
        wk["page-size"] = opts.page
    else:
        if "width" in opts.page:
            wk["page-width"] = str(opts.page["width"])
        if "height" in opts.page:
            wk["page-height"] = str(opts.page["height"])

    # Margins — wkhtmltopdf wants either numeric mm or "0mm" strings
    margin = opts.margin_dict()  # already "0mm"-style
    wk["margin-top"] = margin["top"]
    wk["margin-bottom"] = margin["bottom"]
    wk["margin-left"] = margin["left"]
    wk["margin-right"] = margin["right"]

    if opts.landscape:
        wk["orientation"] = "Landscape"

    return wk


def is_available() -> bool:
    """Is wkhtmltopdf installed and callable?"""
    return shutil.which("wkhtmltopdf") is not None
