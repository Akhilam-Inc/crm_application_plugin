# Copyright (c) 2023, tailorraj and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_data(filters):

	sales_person_sales_data = frappe.db.sql("""
    select 
    si.customer,si.posting_date,sum(sii.amount) as total,sii.custom_sales_person 
    from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.name = sii.parent 
    where sii.custom_sales_person is not null and si.docstatus = 1 {conditions}
    group by si.customer,sii.custom_sales_person 
    order by si.posting_date desc 
    """.format(conditions=get_conditions(filters)),filters,as_dict = 1)

	return sales_person_sales_data

def get_conditions(filters):
	conditions = []
	

	if filters.get("customer"):
		conditions.append("si.customer=%(customer)s")

	if filters.get("sales_person"):
		conditions.append("sii.custom_sales_person=%(sales_person)s")
				
	return "and {}".format(" and ".join(conditions)) if conditions else ""


def get_columns(filters):
	columns =[
		{
			"label":_("Customer"),
			"fieldname": "customer",
			"fieldtype": "Data",
			"width": 220
		},
		{
			"label":_("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label":_("Amount"),
			"fieldname": "total",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label":_("Sales Person"),
			"fieldname": "custom_sales_person",
			"fieldtype": "Data",
			"width": 150
		},
	]
	return columns