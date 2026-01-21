frappe.ui.form.on('Print Migration Job', {
    run_migration: function(frm) {
        frappe.confirm(
            __('Start print format migration? This may take several minutes.'),
            function() {
                frappe.call({
                    method: 'amb_print.tasks.trigger_migration',
                    freeze: true,
                    freeze_message: __('Queueing migration job...'),
                    callback: function(r) {
                        if (r.message && r.message.status === 'queued') {
                            frappe.msgprint(__('Migration job queued. Check status below.'));
                            frm.reload_doc();
                        }
                    }
                });
            }
        );
    },
    
    refresh: function(frm) {
        if (frm.doc.status === 'Running') {
            setTimeout(() => frm.reload_doc(), 5000);
        }
    }
});
