// Phase 11 Skeleton: Labels button on Sales Order
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.is_new()) return;
        
        // Add "Hello World" button - calls server method
        frm.add_custom_button(__('Hello World'), () => {
            frappe.call({
                method: 'amb_print.api.label_hello_world',
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
        
        // Add "Print Hello World" button - opens print format
        frm.add_custom_button(__('Print Hello World'), () => {
            window.open('/api method/print_format.md_to_html?doctype=Sales Order&name=' + frm.docname + '&format=Label Hello World', '_blank');
        }, __('Labels'));
    }
});
