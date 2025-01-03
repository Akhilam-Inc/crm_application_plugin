// Copyright (c) 2023, tailorraj and contributors
// For license information, please see license.txt

frappe.ui.form.on('Aetas CRM Configuration', {
	assign_customer_tier: function(frm) {
		frappe.call({
			"method": "crm_application_plugin.crm_application_plugin.doctype.aetas_crm_configuration.aetas_crm_configuration.enqueue_assign_customer_tier",
			"callback": function(response) {
				if(response.message) {
					frappe.msgprint(__("Customer Tier Assignment has been initiated"));
				}
			}
		})
	}
});
