frappe.ui.form.on('Print Migration Job', {

    // Retired the nightly cron (0 2 * * *) — this is its on-demand replacement.
    // One document, rendered and ATTACHED, with the file_url shown so the operator
    // can see the artefact actually landed rather than trusting a success toast.
    migrate_single_document: function(frm) {
        const d = new frappe.ui.Dialog({
            title: __('Migrate a single document'),
            fields: [
                {fieldname: 'doctype_name', fieldtype: 'Link', options: 'DocType',
                 label: __('Document Type'), reqd: 1},
                {fieldname: 'docname', fieldtype: 'Dynamic Link', options: 'doctype_name',
                 label: __('Document'), reqd: 1}
            ],
            primary_action_label: __('Render & attach'),
            primary_action: function(v) {
                frappe.call({
                    method: 'amb_print.tasks.migrate_single_document',
                    args: {doctype: v.doctype_name, docname: v.docname},
                    freeze: true,
                    freeze_message: __('Rendering...'),
                    callback: function(r) {
                        d.hide();
                        if (r.message && r.message.file_url) {
                            frappe.msgprint(__('Attached: {0}',
                                ['<a href="' + r.message.file_url + '" target="_blank">'
                                 + r.message.file_url + '</a>']));
                        } else {
                            frappe.msgprint(__('Rendered, but nothing was attached — check the log.'));
                        }
                    }
                });
            }
        });
        d.show();
    },
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
