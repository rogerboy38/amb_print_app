"""Batch processor for print format migrations."""

import frappe
from frappe import _


class BatchProcessor:
    """Process documents in batch for PDF generation."""
    
    def __init__(self, api=None):
        self.api = api
    
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
        
        # Get all documents of this type
        docs = frappe.get_all(doctype, limit=100)
        
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
    
    def _process_single_document(self, doctype, docname):
        """Process a single document.
        
        Args:
            doctype: Document type
            docname: Document name
        """
        from frappe.utils.pdf import get_pdf
        
        # Generate HTML
        html = frappe.get_print(doctype, docname)
        
        # Generate PDF using Chromium backend (if configured)
        pdf = get_pdf(html)
        
        return pdf
