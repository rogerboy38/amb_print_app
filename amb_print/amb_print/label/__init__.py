"""
amb_print.label
===============

Label-specific orchestration: HTML build + attach. Public surface:

    from amb_print.label.render import build_html
    from amb_print.label.attach import save_pdf_to_doc

`api.print_label_pdf` is the only intended caller of these. Future label
formats (Label 4, Sample Request labels, etc.) reuse the same two
functions — only the print_format argument changes.
"""

from .render import build_html
from .attach import save_pdf_to_doc

__all__ = ["build_html", "save_pdf_to_doc"]
