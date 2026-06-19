// amb_print — Batch AMB label/scan actions (additive to amb_w_spc batch_amb.js).
// Registered via doctype_js["Batch AMB"]. Generates the Barrel Scan Sheet PDF,
// attaches it to the batch, and downloads it.
frappe.ui.form.on('Batch AMB', {
    refresh(frm) {
        if (frm.is_new()) return;
        frm.add_custom_button(__('Barrel Scan Sheet'), () => {
            frappe.call({
                method: 'amb_print.amb_print.api.print_label_pdf',
                args: {
                    doctype: frm.doc.doctype,
                    docname: frm.docname,
                    print_format: 'Barrel Scan Sheet',
                    save_attachment: 1
                },
                freeze: true,
                freeze_message: __('Generating Barrel Scan Sheet...'),
                callback: function(r) {
                    if (!r.message || !r.message.pdf_base64) return;
                    const bin = atob(r.message.pdf_base64);
                    const bytes = new Uint8Array(bin.length);
                    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
                    const blob = new Blob([bytes], {type: 'application/pdf'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'Barrel-Scan-Sheet-' + frm.docname + '.pdf';
                    document.body.appendChild(a); a.click(); document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    if (r.message.file_url) {
                        frappe.show_alert({message: __('Scan sheet attached to document'), indicator: 'green'});
                        frm.reload_doc();
                    }
                }
            });
        }, __('Labels'));
    }
});
