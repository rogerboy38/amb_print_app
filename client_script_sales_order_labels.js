frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.is_new()) return;
        
        // BUG 92A Fix: Hello World button - calls server method
        frm.add_custom_button(__('Hello World'), function() {
            frappe.call({
                method: 'amb_print.amb_print.api.label_hello_world',
                args: { sales_order: frm.docname },
                callback: function(r) {
                    if (r.message) frappe.msgprint(r.message);
                }
            });
        }, __('Labels'));
        
        // BUG 92B Fix: Print Hello World - uses Frappe's built-in PDF download
        frm.add_custom_button(__('Print Hello World'), function() {
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Hello World`;
            window.open(url, '_blank');
        }, __('Labels'));
    }
});
