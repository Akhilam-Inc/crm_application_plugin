import frappe
from crm_application_plugin.api.utils import create_response


@frappe.whitelist()
def get_assigned_customer_list():
	# user = frappe.session.user
	# Implement Serach Function
	# Get Frappe user from session, Get Employee for that user and fetch sales person for that employee.
	# Get All Customers where the sales person is mentioned in sales team
	try:
		user = frappe.session.user
		employee = frappe.get_value("Employee", {"user_id": user}, "name")
		if not employee:
			create_response(404, "Employee not found for the current user.")
			return

		sales_person = frappe.get_value("Sales Person", {"employee": employee}, "name")
		if not sales_person:
			create_response(404, "Sales Person not found for the current user.")
			return

		customer_data = frappe.db.sql("""
			SELECT c.name, c.customer_name, c.custom_sales_person, c.mobile_no, c.email_id,
			(SELECT MAX(si.posting_date) FROM `tabSales Invoice` si WHERE si.customer = c.customer_name) AS last_purchase_date
			FROM `tabCustomer` c
			WHERE c.custom_sales_person = %s
		""", (sales_person), as_dict=True)

		create_response(200, "Assigned Customer List Fetched!", customer_data)
		return

	except Exception as e:
		create_response(500, "An error occurred while getting assigned customer list", str(e))
		return



@frappe.whitelist()
def get_unassigned_customer_list():
	# Implement Serach Function
	# Get Frappe user from session, Get Employee for that user and fetch sales person for that employee.
	# Get All Customers where the sales person is mentioned in sales team.
	try:
		user = frappe.session.user
		employee = frappe.db.get_value("Employee",{"user_id" : user} ,"name")
		if not employee:
			create_response(404, "Employee not found for the current user.")
			return	

		sales_person = frappe.get_value("Sales Person", {"employee": employee}, "name")	
		if not sales_person:
			create_response(404, "Sales Person not found for the current user.")
			return

		customer_list = frappe.db.sql("""
		select c.name,c.mobile_no from`tabCustomer` c where c.custom_sales_person != %(sales_person)s OR c.custom_sales_person IS NULL			
		""",{'sales_person':sales_person},as_dict = 1)

		if customer_list:
			create_response(200, "Unassigned Customer List Fetched!", customer_list)
			return
		else:
			create_response(406,"getting customer data failed!")
			return	
	except Exception as e:
		create_response(500,"An error occurred while getting assigned customer list",e)	


@frappe.whitelist()
def get_past_purchase_customer():
	try:
		customer = frappe.local.form_dict.customer
		# Get Sales of this customer by based on customer parameter

		customer_sales_data = frappe.db.sql("""
		select si.posting_date,sii.item_name,si.rounded_total
		from`tabSales Invoice` si
		Inner Join`tabSales Invoice Item` sii on si.name = sii.parent
		where si.customer = %(customer_name)s order by si.posting_date desc
		""",{'customer_name':customer},as_dict=1)

		if len(customer_sales_data) > 0:
			create_response(200, "Past Purchase Of Customer List Fetched!", customer_sales_data)
			return
		else:
			create_response(406,"getting customer sales data failed!")
			return
	except Exception as e:
		create_response(500, "An error occurred while fetching customer sales data", e)	

# @frappe.whitelist()
# def get_customers():
# 	try:
# 		customers = frappe.db.sql("""
# 		select customer_name,st.sales_person from`tabCustomer` c Inner Join `tabSales Team` st on c.name = st.parent""",as_dict=1)

# 		customer_data = []

# 		for customer in customers:
# 			customer_address = frappe.db.sql("""
# 			select a.phone, a.email_id from `tabAddress` a left join `tabDynamic Link` dl on dl.parent = a.name and dl.link_doctype = 'Customer' where dl.link_name = %(customer)s
# 			""",{'customer':customer['customer_name']},as_dict = 1)

# 			last_purchase_date = frappe.db.sql("""
# 				select MAX(si.posting_date) AS last_purchase_date from `tabSales Invoice` si where si.customer = %s """, customer['customer_name'], as_dict=1)

# 			customer_info = {
# 				"customer_name": customer['customer_name'],
# 				"number": customer_address[0]['phone'] if customer_address else None,
# 				"email": customer_address[0]['email_id'] if customer_address else None,
# 				"last_purchase_date": last_purchase_date[0]['last_purchase_date'] if last_purchase_date else None
# 			}

# 			customer_data.append(customer_info)

# 		create_response(200, "Customer List Fetched!",customer_data)
# 		return 
# 	except Exception as e:
# 		create_response(406,"getting customer data failed",e)
# 		return


@frappe.whitelist()
def create_customer(customer_name,mobile_number,email_address,date_of_birth,anniversary_date,address_line1,address_line2,city,state,pincode):
	if not customer_name or not mobile_number or not email_address or not address_line1 or not city or not state or not pincode:
		create_response(400, "Invalid request data", "Please provide all mandatory field data.")
		return

	try:
		customer_obj = frappe.get_doc({
			"doctype": "Customer",
			"customer_name":customer_name,
			"customer_type": "Individual",  
			"territory": "All Territories",  
			"customer_group":"Individual",
			"custom_date_of_birth":date_of_birth,
			"custom_anniversary_date":anniversary_date
		})
		customer_doc = customer_obj.insert(ignore_permissions=True)

		contact_doc = frappe.get_doc({
			'doctype':'Contact',
			'first_name':customer_name,
			'email_ids':[
				{'email_id':email_address,
				'is_primary':1}
			],
			'phone_nos':[
				{"phone":mobile_number,
				"is_primary_mobile_no":1}
			],
			'links':[{
				'link_doctype':'Customer',
				'link_name':customer_doc.name

			}]
		})
		
		contact_doc.insert(ignore_permissions=True)

		address_doc = frappe.get_doc({
			'doctype':'Address',
			'address_type':'Billing',
			'address_line1':address_line1,
			'address_line2':address_line2,
			'city':city,
			'state':state,
			'links':[{
				'link_doctype':'Customer',
				'link_name':customer_doc.name

			}]
		})
		address_doc.insert(ignore_permissions = True)
		create_response(200,"customer created successfully")
		return
				
	except Exception as e:
		create_response(406,"customer creation failed",e)
		return



@frappe.whitelist()
def get_customer_detail(customer_name):
	try:
		customer_detail = frappe.db.sql("""
		select c.customer_name,c.custom_date_of_birth,c.custom_anniversary_date,c.custom_sales_person,
		c.mobile_no,c.email_id,c.primary_address
		from `tabCustomer` c 
		where customer_name = %(customer)s""", {'customer': customer_name}, as_dict=1)

		if customer_detail:
			create_response(200, "Customer Fetched!",customer_detail)
			return 
		else:
			create_response(406, "Customer data not found", "Customer data is incomplete or does not exist")
			return
	except Exception as e:
		create_response(500, "Internal server error", str(e))
		return

