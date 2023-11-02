// Copyright (c) 2023, tailorraj and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Aetas Sales by Sales Person"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label":__("Customer"),
			"fieldtype":"Link",
			"options":"Customer"
		},
		{
			"fieldname":"sales_person",
			"label":__("Sales Person"),
			"fieldtype":"Link",
			"options":"Sales Person"
		},
	]
};
