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
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Hello World`;
            window.open(url, '_blank');
        }, __('Labels'));
        
        // Label Small button
        frm.add_custom_button(__('Label Small'), () => {
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Small`;
            window.open(url, '_blank');
        }, __('Labels'));
        
        // Label Medium button
        frm.add_custom_button(__('Label Medium'), () => {
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Medium`;
            window.open(url, '_blank');
        }, __('Labels'));
        
        // Label Large button
        frm.add_custom_button(__('Label Large'), () => {
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Large`;
            window.open(url, '_blank');
        }, __('Labels'));
        
        // Label Export button
        frm.add_custom_button(__('Label Export'), () => {
            const url = `/api/method/frappe.utils.print_format.download_pdf?doctype=${encodeURIComponent(frm.doc.doctype)}&name=${encodeURIComponent(frm.docname)}&format=Label Export`;
            window.open(url, '_blank');
        }, __('Labels'));
    }
});