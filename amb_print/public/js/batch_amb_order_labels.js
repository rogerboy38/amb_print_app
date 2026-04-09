// Phase 11: Label Printing - Batch AMB Labels Button
frappe.ui.form.on('Batch AMB', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Helper function to download PDF
        const downloadPdf = function(printFormat, extraArgs = {}) {
            frappe.call({
                method: 'amb_print.amb_print.api.print_label_pdf',
                args: {
                    doctype: frm.doc.doctype,
                    docname: frm.docname,
                    print_format: printFormat,
                    ...extraArgs
                },
                callback: function(r) {
                    if (r.message && r.message.pdf_base64) {
                        const byteCharacters = atob(r.message.pdf_base64);
                        const byteNumbers = new Array(byteCharacters.length);

                        for (let i = 0; i < byteCharacters.length; i++) {
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }

                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], { type: 'application/pdf' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');

                        a.href = url;
                        a.download = printFormat.replace(/ /g, '-') + '-' + frm.docname + '.pdf';

                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    } else {
                        frappe.msgprint(__('Could not generate PDF.'));
                    }
                },
                error: function() {
                    frappe.msgprint(__('There was an error generating the PDF.'));
                }
            });
        };

        const showSmallLabelDialog = function() {
            const dialog = new frappe.ui.Dialog({
                title: __('Print Label Small 8'),
                fields: [
                    {
                        fieldtype: 'Select',
                        fieldname: 'start_position',
                        label: __('Start Position'),
                        options: [
                            'A1',
                            'B1',
                            'A2',
                            'B2',
                            'A3',
                            'B3',
                            'A4',
                            'B4'
                        ].join('\n'),
                        default: 'A1',
                        reqd: 1,
                        description: __('Choose the first available label position on the sheet.')
                    },
                    {
                        fieldtype: 'Int',
                        fieldname: 'label_qty',
                        label: __('Labels to Print'),
                        default: 1,
                        reqd: 1,
                        description: __('How many labels should be printed starting from that position.')
                    }
                ],
                primary_action_label: __('Print'),
                primary_action(values) {
                    const qty = cint(values.label_qty);

                    if (!qty || qty < 1) {
                        frappe.msgprint(__('Labels to Print must be at least 1.'));
                        return;
                    }

                    if (qty > 8) {
                        frappe.msgprint(__('Labels to Print cannot be more than 8.'));
                        return;
                    }

                    downloadPdf('Label Small 8 Batch', {
                        start_position: values.start_position,
                        label_qty: qty
                    });

                    dialog.hide();
                }
            });

            dialog.show();
        };

        // Label Logo 4 - for preprinted label sheets with logo (4-up)
        frm.add_custom_button(__('Label Logo 4'), () => {
            downloadPdf('Label Logo 4');
        }, __('Labels'));

        // Label Blank 4 - for blank label sheets without logo (4-up)
        frm.add_custom_button(__('Label Blank 4'), () => {
            downloadPdf('Label Blank 4');
        }, __('Labels'));

        // Label Small 8 - for small sample bags (8-up, 2x4) with selectable start position
        frm.add_custom_button(__('Label Small 8'), () => {
            showSmallLabelDialog();
        }, __('Labels'));
    }
});
