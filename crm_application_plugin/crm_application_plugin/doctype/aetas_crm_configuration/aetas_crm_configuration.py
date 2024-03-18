# Copyright (c) 2023, tailorraj and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AetasCRMConfiguration(Document):
	pass


@frappe.whitelist()
def enqueue_assign_customer_tier():
	frappe.enqueue("crm_application_plugin.scheduler_events.crm_events.assign_customer_tier", queue='long')
	return "Task enqueued"

