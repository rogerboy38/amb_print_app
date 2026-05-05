"""
amb_print.pdf
=============

Public API:

    render_pdf(html, **options) -> bytes

Tries Playwright + headless Chromium first (preferred); falls back to
wkhtmltopdf if Chromium isn't available. Raises a Frappe ValidationError
if both paths fail, with diagnostic info attached so the operator can
file a useful bug report.

Why a dispatcher instead of just calling Playwright directly?
    - Lets us swap engines without touching the label/ orchestration layer.
    - Concentrates the fallback logic in one place — the rest of the app
      doesn't need to know wkhtmltopdf still exists.
    - Future renderers (e.g. a Browserless cloud API for very large jobs)
      slot in here without further refactoring.

Disable the fallback (decision #5) by setting:
    frappe.flags.amb_print_disable_wkhtml_fallback = True
or the env var `AMB_PRINT_DISABLE_WKHTML_FALLBACK=1`.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from .options import (
    PdfOptions,
    PageSpec,
    MarginSpec,
    LETTER_PORTRAIT_FULL_BLEED,
    A4_PORTRAIT_FULL_BLEED,
    LETTER_PORTRAIT_1MM,
    from_kwargs,
)

__all__ = [
    "render_pdf",
    "PdfOptions",
    "PageSpec",
    "MarginSpec",
    "LETTER_PORTRAIT_FULL_BLEED",
    "A4_PORTRAIT_FULL_BLEED",
    "LETTER_PORTRAIT_1MM",
]

logger = logging.getLogger(__name__)


def _wkhtml_disabled() -> bool:
    """Has the operator turned off the wkhtmltopdf fallback?"""
    if os.environ.get("AMB_PRINT_DISABLE_WKHTML_FALLBACK", "").lower() in (
        "1", "true", "yes"
    ):
        return True
    try:
        import frappe
        return bool(getattr(frappe.flags, "amb_print_disable_wkhtml_fallback",
                             False))
    except Exception:
        return False


def render_pdf(html: str, options: Optional[PdfOptions] = None,
               **option_overrides) -> bytes:
    """Render HTML to PDF bytes. Try Chromium, then optionally wkhtmltopdf.

    Examples
    --------
    >>> render_pdf(html, page="Letter", margin_mm=0)
    >>> render_pdf(html, options=LETTER_PORTRAIT_FULL_BLEED)
    >>> render_pdf(html, page={"width": "215.9mm", "height": "279.4mm"})
    """
    # ---- Primary: Playwright -------------------------------------------
    chromium_error: Optional[Exception] = None
    try:
        from . import playwright_engine
        return playwright_engine.render_pdf_chromium(
            html, options=options, **option_overrides
        )
    except ImportError as e:
        # playwright package not installed
        chromium_error = e
        logger.warning("amb_print: playwright import failed: %s", e)
    except Exception as e:
        chromium_error = e
        logger.warning("amb_print: chromium render failed: %s", e)

    # ---- Fallback: wkhtmltopdf -----------------------------------------
    if _wkhtml_disabled():
        _throw_render_error(chromium_error, fallback_disabled=True)

    try:
        from . import fallback
        if not fallback.is_available():
            _throw_render_error(chromium_error,
                                fallback_unavailable=True)
        return fallback.render_pdf_wkhtml(
            html, options=options, **option_overrides
        )
    except Exception as wk_err:
        _throw_render_error(chromium_error, wkhtml_error=wk_err)


def _throw_render_error(chromium_error: Optional[Exception], *,
                        fallback_disabled: bool = False,
                        fallback_unavailable: bool = False,
                        wkhtml_error: Optional[Exception] = None) -> None:
    """Raise via frappe.throw with a useful diagnostic payload."""
    parts = ["amb_print: PDF render failed."]
    if chromium_error is not None:
        parts.append(f"Chromium error: {type(chromium_error).__name__}: "
                     f"{chromium_error}")
    if fallback_disabled:
        parts.append("wkhtmltopdf fallback is disabled "
                     "(AMB_PRINT_DISABLE_WKHTML_FALLBACK).")
    if fallback_unavailable:
        parts.append("wkhtmltopdf binary not found on PATH.")
    if wkhtml_error is not None:
        parts.append(f"wkhtmltopdf error: {type(wkhtml_error).__name__}: "
                     f"{wkhtml_error}")
    parts.append("Hint: ensure `playwright install chromium` has run "
                 "and PLAYWRIGHT_BROWSERS_PATH is set correctly.")

    msg = "\n".join(parts)
    try:
        import frappe
        frappe.throw(msg, title="amb_print PDF render failed")
    except ImportError:
        # Outside a Frappe context (CLI tests) — re-raise raw
        raise RuntimeError(msg)
