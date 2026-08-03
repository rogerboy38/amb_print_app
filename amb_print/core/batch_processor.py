"""Batch processor for print format migrations."""

import frappe
from frappe import _


class BatchProcessor:
    """Process documents in batch for PDF generation."""
    
    DEFAULT_BATCH_LIMIT = 100

    def __init__(self, api=None, batch_limit=None):
        self.api = api
        self.batch_limit = batch_limit or self.DEFAULT_BATCH_LIMIT
    
    def process_document_type(self, doctype):
        """Process all documents of a given type.
        
        Args:
            doctype: The DocType to process
            
        Returns:
            dict: Processing results
        """
        results = {
            "doctype": doctype,
            "processed": 0,
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        # LIMIT is not just a cap, it is a NON-DETERMINISTIC cap: `limit=100` with no
        # `order_by` returns an arbitrary 100 of N, so two runs can cover different
        # documents and neither ever converges. Order it, and REPORT what was skipped —
        # silent truncation reads as "covered everything".
        total = frappe.db.count(doctype)
        docs = frappe.get_all(doctype, limit=self.batch_limit, order_by="modified asc")
        results["total_available"] = total
        results["skipped"] = max(0, total - len(docs))
        if results["skipped"]:
            frappe.logger().warning(
                "amb_print: %s — processed %s of %s, SKIPPED %s (batch_limit=%s)"
                % (doctype, len(docs), total, results["skipped"], self.batch_limit)
            )

        for doc in docs:
            results["processed"] += 1
            try:
                self._process_single_document(doctype, doc.name)
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "name": doc.name,
                    "error": str(e)
                })

        return results
    
    def _process_single_document(self, doctype, docname, attach=True):
        """Render one document to PDF and ATTACH it to that document.

        Previously this returned the PDF and every caller dropped the return value —
        so the nightly job rendered up to 100 PDFs per doctype through Chromium and
        threw all of them away. `ERPNextAPI.upload_file` exists but is called from
        nowhere in core/, so nothing had ever persisted a render.

        We attach via `save_file` rather than returning bytes for download: the purpose
        of a migration is that the artefact EXISTS afterwards. A download hands bytes to
        whoever clicked and leaves the record unchanged — the next person sees nothing,
        and there is no evidence the migration ran. Attachment makes the result
        inspectable, makes idempotency checkable, and gives the operation a before/after.
        A download can be added on top of a persisted file; it must not replace it.

        Returns:
            dict: {"pdf": bytes, "file_url": str|None, "attached": bool}
        """
        from frappe.utils.pdf import get_pdf
        from frappe.utils.file_manager import save_file

        html = frappe.get_print(doctype, docname)
        pdf = get_pdf(html)

        file_url = None
        if attach:
            fname = "%s-%s.pdf" % (doctype.replace(" ", "_"), docname)
            f = save_file(fname, pdf, doctype, docname, is_private=1)
            file_url = f.file_url

        return {"pdf": pdf, "file_url": file_url, "attached": bool(file_url)}
