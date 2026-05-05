"""
amb_print.pdf.options
=====================

Options dataclass for the amb_print rendering pipeline plus a Letter-portrait
recipe used by label printing.

Why this module exists
----------------------
We deliberately avoid the wkhtmltopdf-style hyphenated keys (`margin-top`,
`page-width`, …) that print_designer's `Browser.prepare_options_for_pdf()`
expects. Our keys are plain Python attributes consumed directly by
`pdf.playwright_engine.render_pdf_chromium()` and translated to Playwright's
`page.pdf()` kwargs there. This keeps the public API explicit and avoids the
double-translation pitfalls documented in the chrome_pdf_margins research:

    options dict (hyphen) -> updated_options dict (camelCase) -> CDP

If we ever need to feed wkhtmltopdf as a fallback we translate at the
fallback boundary (see `pdf.fallback.render_pdf_wkhtml`), not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Union

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

# Page can be a named format ("Letter", "A4") or an explicit size dict
# {"width": "215.9mm", "height": "279.4mm"}. Mirrors Playwright's API.
PageSpec = Union[str, Dict[str, str]]

# Margin can be a uniform integer in mm, or a per-side dict
# {"top": 0, "bottom": 0, "left": 0, "right": 0}.
MarginSpec = Union[int, Dict[str, int]]


# ---------------------------------------------------------------------------
# PdfOptions dataclass
# ---------------------------------------------------------------------------

@dataclass
class PdfOptions:
    """Options for amb_print's PDF rendering pipeline.

    Attributes
    ----------
    page : PageSpec
        Either a named Playwright format (e.g. "Letter", "A4", "Legal") or an
        explicit size dict {"width": "215.9mm", "height": "279.4mm"}.
        Defaults to "Letter".

    margin_mm : MarginSpec
        Uniform margin in mm (int) or per-side dict.
        Defaults to 0 (full bleed).

    prefer_css_page_size : bool
        When True, Chrome honors `@page { size: ...; margin: ... }` declared
        in the HTML and ignores `page` / `margin_mm` from this dataclass.
        Defaults to True — our label templates declare their own @page rules
        and we want them to win.

    print_background : bool
        Render CSS `background-color` / `background-image`.
        Defaults to True (most label designs assume backgrounds print).

    wait_until : str
        Playwright's wait condition before snapshotting. "networkidle" is
        safest for templates with web fonts or barcode images. Use "load"
        or "domcontentloaded" for faster renders when no external resources
        are involved.
        Defaults to "networkidle".

    timeout_ms : int
        Hard cap on a single render (ms). Defaults to 30000 (30s).

    landscape : bool
        Force landscape orientation. Usually False; templates flip via @page.
    """

    page: PageSpec = "Letter"
    margin_mm: MarginSpec = 0
    prefer_css_page_size: bool = True
    print_background: bool = True
    wait_until: str = "networkidle"
    timeout_ms: int = 30000
    landscape: bool = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def margin_dict(self) -> Dict[str, str]:
        """Return margins as a Playwright-shaped dict of CSS strings."""
        if isinstance(self.margin_mm, int):
            value = max(0, int(self.margin_mm))
            return {k: f"{value}mm" for k in ("top", "bottom", "left", "right")}
        # dict path — accept ints or numeric strings
        out: Dict[str, str] = {}
        for side in ("top", "bottom", "left", "right"):
            v = self.margin_mm.get(side, 0)
            try:
                v_int = max(0, int(v))
            except (TypeError, ValueError):
                v_int = 0
            out[side] = f"{v_int}mm"
        return out

    def to_playwright_kwargs(self) -> Dict[str, object]:
        """Translate this dataclass to a kwargs dict for `Page.pdf(...)`.

        The caller (playwright_engine) unpacks this directly — keeps the
        translation logic in one place.
        """
        kwargs: Dict[str, object] = {
            "margin": self.margin_dict(),
            "prefer_css_page_size": self.prefer_css_page_size,
            "print_background": self.print_background,
            "landscape": self.landscape,
        }
        if isinstance(self.page, str):
            kwargs["format"] = self.page
        elif isinstance(self.page, dict):
            # Explicit width/height — do NOT pass `format` (Playwright errors
            # if both are supplied).
            for k in ("width", "height"):
                if k in self.page:
                    kwargs[k] = self.page[k]
        return kwargs


# ---------------------------------------------------------------------------
# Recipes — frozen, ready-to-use option sets
# ---------------------------------------------------------------------------

#: US Letter portrait, full bleed, CSS @page wins. The default for amb_print
#: labels: matches the Label Small 8 (Container) template's own @page rule
#: of `size: 215.9mm 279.4mm; margin: 0`.
LETTER_PORTRAIT_FULL_BLEED = PdfOptions(
    page="Letter",
    margin_mm=0,
    prefer_css_page_size=True,
    print_background=True,
    landscape=False,
)

#: A4 portrait, full bleed. For non-US label stock.
A4_PORTRAIT_FULL_BLEED = PdfOptions(
    page="A4",
    margin_mm=0,
    prefer_css_page_size=True,
    print_background=True,
    landscape=False,
)

#: Letter portrait with 1mm safety margin — use if your printer driver
#: refuses true 0mm. Some inkjets clip the last 0.5mm of every edge anyway,
#: so a 1mm gutter is a reasonable defensive default for physical printing.
LETTER_PORTRAIT_1MM = PdfOptions(
    page="Letter",
    margin_mm=1,
    prefer_css_page_size=False,  # force this margin even if CSS says 0
    print_background=True,
    landscape=False,
)


def from_kwargs(**kwargs) -> PdfOptions:
    """Build a PdfOptions from loose kwargs, ignoring unknown keys.

    Convenience for the public API: `render_pdf(html, page="Letter", margin_mm=0)`
    becomes `from_kwargs(page="Letter", margin_mm=0)` internally.
    """
    valid = {f for f in PdfOptions.__dataclass_fields__}
    filtered = {k: v for k, v in kwargs.items() if k in valid}
    return PdfOptions(**filtered)
