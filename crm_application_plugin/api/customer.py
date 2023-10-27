import frappe
from crm_application_plugin.api.utils import create_response

@frappe.whitelist()
def get_customers():
	try:
		customers = frappe.db.sql("""
		select customer_name,st.sales_person from`tabCustomer` c Inner Join `tabSales Team` st on c.name = st.parent""",as_dict=1)

		customer_data = []

		for customer in customers:
			customer_address = frappe.db.sql("""
			select a.phone, a.email_id from `tabAddress` a left join `tabDynamic Link` dl on dl.parent = a.name and dl.link_doctype = 'Customer' where dl.link_name = %(customer)s
			""",{'customer':customer['customer_name']},as_dict = 1)

			last_purchase_date = frappe.db.sql("""
				select MAX(si.posting_date) AS last_purchase_date from `tabSales Invoice` si where si.customer = %s """, customer['customer_name'], as_dict=1)

			customer_info = {
				"customer_name": customer['customer_name'],
				"number": customer_address[0]['phone'] if customer_address else None,
				"email": customer_address[0]['email_id'] if customer_address else None,
				"last_purchase_date": last_purchase_date[0]['last_purchase_date'] if last_purchase_date else None
			}

			customer_data.append(customer_info)

		return customer_data 
	except Exception as e:
		create_response(406,"getting customer data failed",e)


@frappe.whitelist()
def create_customer():
	try:
		customer_name = frappe.local.form_dict.customer
		if frappe.db.exists("Customer",{'customer_name':customer_name}):
			return create_response(403,"customer already exists in data",{customer_name})
		
		mobile_no = frappe.local.form_dict.mobile_no
		email_address = frappe.local.form_dict.email_address
		# address_data = frappe.local.form_dict.address

		
		customer_obj = frappe.get_doc({
			"doctype": "Customer",
			"customer_name":customer_name,
			"customer_type": "Individual",  
			"territory": "All Territories",  
			"customer_group":"Individual",

		})
		customer_doc = customer_obj.insert(ignore_permissions=True)

		contact_doc = frappe.get_doc({
			'doctype':'Contact',
			'first_name':customer_name,
		})
		contact_doc.append("email_ids",{
			'email_id':email_address,
			'is_primary':"1"
		})
		contact_doc.append("phone_nos",{
			'phone':mobile_no,
			'is_primary_mobile_no':"1"
		})
		contact_doc.append("links", {
			"link_doctype": "Customer",
			"link_name": customer_doc.name,
		})

		contact_doc.insert(ignore_permissions=True)
		# address = frappe.get_doc({
		# "doctype": "Address",
		# "address_type": "Billing",  
		# "address_line1": address_data,
		# "email_id":email_address,
		# "phone":mobile_no
		# })
		# address.append("links", {
		# 	"link_doctype": "Customer",
		# 	"link_name": customer_name,
		# })
		# address.insert(ignore_permissions=True)
		create_response(200,"customer created successfully",{})
				
	except Exception as e:
		create_response(406,"customer creation failed",e)



@frappe.whitelist()
def get_customer_detail(customer_name):
	try:
		customer_detail = frappe.db.sql("""
			select c.customer_name, st.sales_person,c.custom_date_of_birth,c.custom_anniversary_date
			from `tabCustomer` c 
			Inner Join `tabSales Team` st on c.name = st.parent 
			where customer_name = %(customer)s""", {'customer': customer_name}, as_dict=1)

		customer_address_detail = frappe.db.sql("""
			select a.address_line1, a.address_line2, a.city, a.state, a.country, a.pincode, a.phone, a.email_id
			from `tabAddress` a
			left join `tabDynamic Link` dl on dl.parent = a.name and dl.link_doctype = 'Customer'
			where dl.link_name = %(customer)s
		""", {'customer': customer_name}, as_dict=1)

		customer_contact_detail = frappe.db.sql("""
		select c.email_id,c.phone
		from`tabContact` c
		left join `tabDynamic Link` dl on dl.parent = c.name and dl.link_doctype = 'Customer'
		where dl.link_name = %(customer)s	
		""",{'customer': customer_name},as_dict=1)

		customer_data = []

		if customer_detail:
			address_components = [
				customer_address_detail[0]['address_line1'],
				customer_address_detail[0]['address_line2'],
				customer_address_detail[0]['city'],
				customer_address_detail[0]['state'],
				customer_address_detail[0]['country'],
				customer_address_detail[0]['pincode']
			]

			address = ", ".join(filter(None, address_components))

			customer_info = {
				"customer_name": customer_detail[0]['customer_name'] if customer_detail else ' ',
				"date_of_birth":customer_detail[0]['custom_date_of_birth'] or ' ',
				"anniversary_date": customer_detail[0]['custom_anniversary_date'] or ' ',
				"sales_person": customer_detail[0]['sales_person'] if customer_detail else ' ',
				"address": address if customer_address_detail else '',
				"email_address":customer_contact_detail[0]['email_id'] if customer_contact_detail else '',
				"phone":customer_contact_detail[0]['phone']if customer_contact_detail else ''
			}

			customer_data.append(customer_info)

			return customer_data
		else:
			create_response(406, "Customer data not found", "Customer data is incomplete or does not exist")
	except Exception as e:
		create_response(500, "Internal server error", str(e))
