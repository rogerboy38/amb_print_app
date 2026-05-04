frappe.ui.form.on("Sample Request AMB", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(
                __("Generate Label Cells / Generar Etiquetas"),
                () => generate_label_cells(frm),
                __("Labels / Etiquetas")
            );
        }
    },
});

function generate_label_cells(frm) {
    if (!frm.doc.samples || frm.doc.samples.length === 0) {
        frappe.msgprint({
            title: __("No Samples"),
            message: __("Add at least one row to the Samples table before generating labels."),
            indicator: "orange",
        });
        return;
    }

    const proceed = () => {
        frappe.call({
            method: "amb_print.amb_print.api.generate_label_cells",
            args: { sr_name: frm.doc.name },
            freeze: true,
            freeze_message: __("Generating label cells..."),
            callback: (r) => {
                if (r.message) {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __("Created {0} label cells", [r.message.created]),
                        indicator: "green",
                    });
                    if (r.message.warning) {
                        frappe.msgprint({
                            title: __("Note"),
                            message: r.message.warning,
                            indicator: "orange",
                        });
                    }
                }
            },
        });
    };

    if ((frm.doc.label_cells || []).length > 0) {
        frappe.confirm(
            __("Existing label cells will be replaced. Continue?"),
            proceed,
        );
    } else {
        proceed();
    }
}
