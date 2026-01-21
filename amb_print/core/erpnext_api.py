"""ERPNext API client for remote operations."""

import requests
import frappe


class ERPNextAPI:
    """API client for ERPNext REST operations."""
    
    def __init__(self, base_url=None, api_key=None, api_secret=None):
        self.base_url = base_url or ""
        self.api_key = api_key or ""
        self.api_secret = api_secret or ""
        self.session = requests.Session()
        
        if self.api_key and self.api_secret:
            self.session.headers.update({
                "Authorization": f"token {self.api_key}:{self.api_secret}"
            })
    
    def get_document(self, doctype, docname):
        """Fetch a document from ERPNext.
        
        Args:
            doctype: Document type
            docname: Document name
            
        Returns:
            dict: Document data
        """
        url = f"{self.base_url}/api/resource/{doctype}/{docname}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json().get("data", {})
    
    def get_print_format(self, doctype, docname, print_format=None):
        """Get print HTML for a document.
        
        Args:
            doctype: Document type
            docname: Document name
            print_format: Optional print format name
            
        Returns:
            str: HTML content
        """
        url = f"{self.base_url}/api/method/frappe.www.printview.get_html_and_style"
        params = {
            "doc": docname,
            "doctype": doctype,
            "print_format": print_format or "Standard"
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get("message", {}).get("html", "")
    
    def upload_file(self, file_path, attached_to_doctype=None, attached_to_name=None):
        """Upload a file to ERPNext.
        
        Args:
            file_path: Local file path
            attached_to_doctype: Optional doctype to attach to
            attached_to_name: Optional document name to attach to
            
        Returns:
            dict: Upload result
        """
        url = f"{self.base_url}/api/method/upload_file"
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {}
            if attached_to_doctype:
                data["doctype"] = attached_to_doctype
            if attached_to_name:
                data["docname"] = attached_to_name
            
            response = self.session.post(url, files=files, data=data)
            response.raise_for_status()
            return response.json().get("message", {})
