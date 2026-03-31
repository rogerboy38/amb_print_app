// Phase 11: Label Printing - Sales Order Labels Button
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.is_new()) return;
        
        // Add "Hello World" button - calls server method (testing)
        frm.add_custom_button(__('Hello World'), () => {
            frappe.call({
                method: 'amb_print.amb_print.api.label_hello_world',
                args: {
                    sales_order: frm.docname
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint(r.message);
                    }
                }
            });
        }, __('Labels'));
        
        // Add "Print Hello World" button - downloads PDF with 4-up label layout
        frm.add_custom_button(__('Print Hello World'), () => {
            // Use server method to avoid whitelist error (BUG 93C fix)
            frappe.call({
                method: 'amb_print.amb_print.api.print_label_pdf',
                args: {
                    doctype: frm.doc.doctype,
                    docname: frm.docname,
                    print_format: 'Label Hello World'
                },
                callback: function(r) {
                    if (r.message && r.message.pdf_base64) {
                        // Convert base64 to blob and download
                        const byteCharacters = atob(r.message.pdf_base64);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], {type: 'application/pdf'});
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'Label-' + frm.docname + '.pdf';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }
                }
            });
        }, __('Labels'));
    }
});