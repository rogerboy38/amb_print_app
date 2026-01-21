import frappe
from frappe import _
from frappe.utils import now_datetime
import time


def scheduled_batch_migration():
    """Scheduled task for automated batch migration."""
    job_doc = frappe.get_single("Print Migration Job")
    
    if job_doc.status == "Running":
        frappe.log_error("Migration already running", "Print Migration")
        return
    
    run_migration_job()


def run_migration_job():
    """Main migration job - runs in background."""
    job_doc = frappe.get_single("Print Migration Job")
    job_doc.status = "Running"
    job_doc.last_run = now_datetime()
    job_doc.progress = 0
    job_doc.save()
    frappe.db.commit()
    
    try:
        from amb_print.core.batch_processor import BatchProcessor
        from amb_print.core.erpnext_api import ERPNextAPI
        
        config = frappe.get_site_config()
        api_config = config.get("amb_print", {})
        
        api = ERPNextAPI(
            base_url=api_config.get("base_url"),
            api_key=api_config.get("api_key"),
            api_secret=api_config.get("api_secret")
        )
        
        doc_types = [d.document_type for d in job_doc.document_types]
        
        processor = BatchProcessor(api)
        total = len(doc_types) if doc_types else 1
        
        for idx, doc_type in enumerate(doc_types):
            job_doc.reload()
            job_doc.progress = (idx / total) * 100
            job_doc.save()
            frappe.db.commit()
            
            start_time = time.time()
            try:
                result = processor.process_document_type(doc_type)
                create_migration_log(
                    document_type=doc_type,
                    status="Success",
                    processing_time=time.time() - start_time
                )
            except Exception as e:
                create_migration_log(
                    document_type=doc_type,
                    status="Failed",
                    error_message=str(e),
                    processing_time=time.time() - start_time
                )
        
        job_doc.reload()
        job_doc.status = "Completed"
        job_doc.progress = 100
        job_doc.save()
        
    except Exception as e:
        job_doc.reload()
        job_doc.status = "Failed"
        job_doc.save()
        frappe.log_error(str(e), "Print Migration Error")
    
    frappe.db.commit()


def create_migration_log(**kwargs):
    """Create a migration log entry."""
    log = frappe.new_doc("Print Migration Log")
    log.update(kwargs)
    log.insert()
    frappe.db.commit()


@frappe.whitelist()
def trigger_migration():
    """API endpoint to trigger migration from UI button."""
    frappe.enqueue(
        "amb_print.tasks.run_migration_job",
        queue="print_migration",
        timeout=3600,
        job_name="print_format_migration"
    )
    return {"status": "queued", "message": _("Migration job queued")}
