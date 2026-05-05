"""
amb_print.pdf.playwright_engine
================================

Primary HTML -> PDF renderer for amb_print, using Playwright + headless
Chromium. Bypasses Frappe's print_designer pipeline entirely:

    HTML string -> Playwright Page.set_content -> Page.pdf -> bytes

No `frappe.get_print()`, no `print_designer.pdf_generator.pdf.get_pdf`,
no CDP-injected `@page` rules competing with our template's own CSS.

References
----------
- Playwright Python docs: https://playwright.dev/python/docs/api/class-page#page-pdf
- Issue #437 in print_designer (Chromium path in Docker): bake into image,
  set PLAYWRIGHT_BROWSERS_PATH explicitly so all bench workers share it.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Optional

from .options import PdfOptions, from_kwargs

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Browser path
# ---------------------------------------------------------------------------
# Set BEFORE `from playwright.sync_api import sync_playwright`. Playwright
# reads this env var on import to decide where to look for chromium-*.
PLAYWRIGHT_BROWSERS_PATH = os.environ.get(
    "PLAYWRIGHT_BROWSERS_PATH",
    "/home/frappe/frappe-bench/playwright-browsers",
)
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", PLAYWRIGHT_BROWSERS_PATH)


# ---------------------------------------------------------------------------
# Concurrency cap
# ---------------------------------------------------------------------------
# Each render spins up a Chromium process (~150 MB resident). On a small
# bench worker, more than ~2 concurrent renders thrashes CPU and bloats
# memory. Configurable via env var `AMB_PRINT_MAX_RENDERS`.
_MAX_CONCURRENT = max(1, int(os.environ.get("AMB_PRINT_MAX_RENDERS", "2")))
_render_semaphore = threading.Semaphore(_MAX_CONCURRENT)


# ---------------------------------------------------------------------------
# Public renderer
# ---------------------------------------------------------------------------

def render_pdf_chromium(html: str, options: Optional[PdfOptions] = None,
                        **option_overrides) -> bytes:
    """Render an HTML string to PDF bytes via headless Chromium (Playwright).

    Parameters
    ----------
    html
        Complete HTML document. Must include <html><head><body>. Use
        `amb_print.label.render.build_html` to construct one from a
        Frappe Print Format.
    options
        Optional pre-built `PdfOptions`. If omitted, sensible defaults
        (Letter, full-bleed, prefer CSS @page, print backgrounds) are used.
    **option_overrides
        Convenience kwargs forwarded to `from_kwargs`. Example:
        `render_pdf_chromium(html, page="Letter", margin_mm=0)`.

    Returns
    -------
    bytes
        PDF content. Empty bytes on failure (caller should check len() and
        fall back to `pdf.fallback.render_pdf_wkhtml` if needed).

    Raises
    ------
    PlaywrightError, OSError
        Surfaced unmodified so the caller can decide whether to fall back
        or to bubble up to `frappe.throw`.
    """
    # Build options first so any silly kwargs error before launching Chromium
    if options is None:
        options = from_kwargs(**option_overrides)
    elif option_overrides:
        # merge: explicit kwargs win over the supplied dataclass
        merged = {f: getattr(options, f) for f in options.__dataclass_fields__}
        merged.update(option_overrides)
        options = from_kwargs(**merged)

    pdf_kwargs = options.to_playwright_kwargs()

    # Lazy import: keeps module-level import cheap if Playwright isn't
    # installed yet (e.g. during initial app discovery / `bench install-app`).
    from playwright.sync_api import sync_playwright

    with _render_semaphore:
        logger.debug("amb_print: launching chromium for render (%s, %s)",
                     options.page, options.margin_mm)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                args=[
                    "--no-sandbox",            # required: bench runs as non-root frappe user
                    "--disable-dev-shm-usage", # fallback if /dev/shm < 64MB (small Docker)
                    "--disable-gpu",           # not useful in a server context
                    "--font-render-hinting=none",  # keep fonts crisp at print DPI
                ],
            )
            try:
                ctx = browser.new_context()
                page = ctx.new_page()
                page.set_default_timeout(options.timeout_ms)
                page.set_content(html, wait_until=options.wait_until,
                                 timeout=options.timeout_ms)
                pdf_bytes = page.pdf(**pdf_kwargs)
            finally:
                browser.close()

    logger.info("amb_print: rendered %d byte PDF via Playwright", len(pdf_bytes))
    return pdf_bytes


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """Quick check: can we launch headless Chromium right now?

    Used by the dispatcher in `pdf.__init__` to decide whether to attempt
    Playwright at all, or skip straight to the wkhtmltopdf fallback.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("amb_print: playwright package not installed")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            browser.close()
        return True
    except Exception as e:
        logger.warning("amb_print: chromium not launchable: %s", e)
        return False
