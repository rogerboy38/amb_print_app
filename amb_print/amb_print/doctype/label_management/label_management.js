frappe.ui.form.on('Label Management', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Print Labels'), function() {
                if (!frm.doc.source_doctype || !frm.doc.source_docname) {
                    frappe.msgprint(__('Please select Source DocType and Source Document first.'));
                    return;
                }
                if (!frm.doc.print_format) {
                    frappe.msgprint(__('Please select a Print Format.'));
                    return;
                }
                // Use Frappe's built-in print/download
                var w = window.open(
                    frappe.urllib.get_full_url(
                        '/api/method/frappe.utils.print_format.download_pdf?'
                        + 'doctype=' + encodeURIComponent(frm.doc.source_doctype)
                        + '&name=' + encodeURIComponent(frm.doc.source_docname)
                        + '&format=' + encodeURIComponent(frm.doc.print_format)
                        + '&no_letterhead=0'
                    )
                );
                if (!w) {
                    frappe.msgprint(__('Please allow pop-ups to download the PDF.'));
                }
            }).addClass('btn-primary');
        }
    }
});
