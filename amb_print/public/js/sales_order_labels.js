// Phase 11: Label Printing - Sales Order Labels Button
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.is_new()) return;
        
        // Helper function to download PDF
        const downloadPdf = function(printFormat) {
            frappe.call({
                method: 'amb_print.amb_print.api.print_label_pdf',
                args: {
                    doctype: frm.doc.doctype,
                    docname: frm.docname,
                    print_format: printFormat
                },
                callback: function(r) {
                    if (r.message && r.message.pdf_base64) {
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
                        a.download = printFormat.replace(/ /g, '-') + '-' + frm.docname + '.pdf';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }
                }
            });
        };
        
        // Label Logo 4 - for preprinted label sheets with logo (4-up)
        frm.add_custom_button(__('Label Logo 4'), () => {
            downloadPdf('Label Logo 4');
        }, __('Labels'));
        
        // Label Blank 4 - for blank label sheets without logo (4-up)
        frm.add_custom_button(__('Label Blank 4'), () => {
            downloadPdf('Label Blank 4');
        }, __('Labels'));
                // Label Small 8 - for small sample bags (8-up, 2x4)
        frm.add_custom_button(__('Label Small 8'), () => {
            downloadPdf('Label Small 8');
        }, __('Labels'));

    }
});
