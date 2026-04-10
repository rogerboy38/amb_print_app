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
                frappe.call({
                    method: 'amb_print.amb_print.api.print_label_pdf',
                    args: {
                        doctype: frm.doc.source_doctype,
                        docname: frm.doc.source_docname,
                        print_format: frm.doc.print_format,
                        start_position: frm.doc.start_position || 'A1',
                        label_qty: frm.doc.label_qty || 8
                    },
                    freeze: true,
                    freeze_message: __('Generating PDF...'),
                    callback: function(r) {
                        if (r.message && r.message.pdf_base64) {
                            var binary = atob(r.message.pdf_base64);
                            var len = binary.length;
                            var bytes = new Uint8Array(len);
                            for (var i = 0; i < len; i++) {
                                bytes[i] = binary.charCodeAt(i);
                            }
                            var blob = new Blob([bytes], {type: 'application/pdf'});
                            var url = URL.createObjectURL(blob);
                            window.open(url);
                        } else {
                            frappe.msgprint(__('Failed to generate PDF.'));
                        }
                    }
                });
            }).addClass('btn-primary');
        }
    }
});
