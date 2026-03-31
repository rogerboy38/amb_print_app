// Phase 11 Skeleton: Labels button on Sales Order
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.is_new()) return;
        
        // Add "Hello World" button - calls server method
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
        
        // Add "Print Hello World" button - uses Frappe's built-in PDF download
        frm.add_custom_button(__('Print Hello World'), () => {
            // Use Frappe's built-in PDF download API (fixes BUG 92B)
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Hello World`;
            window.open(url, '_blank');
        }, __('Labels'));
    }
});
