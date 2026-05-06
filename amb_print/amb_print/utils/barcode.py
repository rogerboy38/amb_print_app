"""
amb_print.utils.barcode
=======================

Inline-SVG Code 128 generator for label print formats. Returns a self-contained
`<svg>` element (no XML/DOCTYPE preamble) so it can be embedded directly into
HTML rendered by Chromium for PDF output.

Used from Jinja templates via:

    {% set _b = frappe.get_attr("amb_print.amb_print.utils.barcode.code128_svg") %}
    {{ _b(row.barrel_serial_number) | safe }}

Requires `python-barcode` to be installed in the Frappe env (baked into the
custom-erpnext:v16.1+ image; `pip install python-barcode` if missing).
"""

from __future__ import annotations

import io
import re

_XML_DECL_RE = re.compile(r"<\?xml[^?]*\?>", re.DOTALL)
_DOCTYPE_RE = re.compile(r"<!DOCTYPE[^>]*>", re.DOTALL)


def code128_svg(
    value: str,
    module_height: float = 12.0,
    module_width: float = 0.30,
    font_size: int = 8,
    text_distance: float = 2.0,
    quiet_zone: float = 1.0,
    write_text: bool = True,
) -> str:
    """Render `value` as a Code 128 barcode and return inline SVG.

    Empty `value` returns an empty string (so the template can call this
    unconditionally without guarding for None). If `python-barcode` is not
    installed, returns a visible red placeholder SVG so the missing
    dependency is obvious during print preview rather than silently hidden.

    Parameters
    ----------
    value : str
        Text to encode. Code 128 supports the full ASCII range.
    module_height : float
        Bar height in millimeters. Default 12mm fits a 4-up label cell.
    module_width : float
        Bar width in millimeters. 0.30mm = ~12 mil, scannable at typical
        warehouse handheld distance (15-30 cm).
    font_size : int
        Human-readable interpretation (HRI) text size in points.
    text_distance : float
        Vertical gap between bars and HRI text in millimeters.
    quiet_zone : float
        Required white margin on each side, in millimeters.
    write_text : bool
        Whether to draw the HRI text below the bars.
    """
    if not value:
        return ""

    try:
        import barcode
        from barcode.writer import SVGWriter
    except ImportError:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="40mm" height="10mm">'
            '<text x="2" y="12" fill="#c00000" font-family="Arial" '
            'font-size="9pt">[python-barcode not installed]</text>'
            "</svg>"
        )

    buf = io.BytesIO()
    options = {
        "module_height": module_height,
        "module_width": module_width,
        "font_size": font_size,
        "text_distance": text_distance,
        "quiet_zone": quiet_zone,
        "write_text": write_text,
    }
    barcode.Code128(str(value), writer=SVGWriter()).write(buf, options=options)
    svg = buf.getvalue().decode("utf-8")
    svg = _XML_DECL_RE.sub("", svg, count=1)
    svg = _DOCTYPE_RE.sub("", svg, count=1)
    return svg.strip()
