// amb_print — Sample Request AMB label/document actions (doctype_js).
// Phase 4: Shipping Label button (small label + shipping documents added in later phases).
frappe.ui.form.on('Sample Request AMB', {
    refresh(frm) {
        if (frm.is_new()) return;
        const gen = (print_format, fname) => {
            frappe.call({
                method: 'amb_print.amb_print.api.print_label_pdf',
                args: { doctype: frm.doc.doctype, docname: frm.docname, print_format: print_format, save_attachment: 1 },
                freeze: true,
                freeze_message: __('Generating {0}...', [print_format]),
                callback: function(r) {
                    if (!r.message || !r.message.pdf_base64) return;
                    const bin = atob(r.message.pdf_base64);
                    const bytes = new Uint8Array(bin.length);
                    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                    const url = URL.createObjectURL(new Blob([bytes], {type: 'application/pdf'}));
                    const a = document.createElement('a');
                    a.href = url; a.download = fname + '-' + frm.docname + '.pdf';
                    document.body.appendChild(a); a.click(); document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    if (r.message.file_url) {
                        frappe.show_alert({message: __('{0} attached', [print_format]), indicator: 'green'});
                        frm.reload_doc();
                    }
                }
            });
        };
        frm.add_custom_button(__('Shipping Label'), () => gen('Shipping Label AMB', 'Shipping-Label'), __('Labels'));
    }
});
