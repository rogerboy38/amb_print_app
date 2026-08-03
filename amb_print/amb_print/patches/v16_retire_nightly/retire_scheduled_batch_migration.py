"""Retire the nightly batch-migration Scheduled Job Type.

THE SECOND HALF. Removing `scheduler_events` from hooks.py stops the hook being
*declared*; it does NOT retire the `Scheduled Job Type` row that a previous migrate
already created. That row keeps firing on its cron. Both halves must travel in one
change or nothing changes on a tier that has already run migrate.

(Same class as a fixture-defined Client Script surviving a DB delete, pointed the
other way: there the fixture resurrects a deleted row; here the row outlives a
deleted hook.)

Idempotent: no row -> nothing to do; already stopped -> nothing to do.
Direction: the job goes from ENABLED to STOPPED. No document data is touched.
"""

import frappe

METHOD = "amb_print.tasks.scheduled_batch_migration"


def execute():
	if not frappe.db.exists("DocType", "Scheduled Job Type"):
		return

	rows = frappe.get_all(
		"Scheduled Job Type",
		filters={"method": METHOD},
		fields=["name", "stopped"],
	)
	if not rows:
		return

	for r in rows:
		if r.stopped:
			continue
		frappe.db.set_value("Scheduled Job Type", r.name, "stopped", 1, update_modified=True)
		frappe.logger().info(
			"amb_print: stopped Scheduled Job Type %s (%s) — nightly batch migration retired"
			% (r.name, METHOD)
		)
