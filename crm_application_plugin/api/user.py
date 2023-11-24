import frappe
from crm_application_plugin.api.utils import create_response

@frappe.whitelist()
def get_user_details():
	try:
		user = frappe.session.user
		employee = frappe.get_value("Employee", {"user_id": user}, "name")
		if not employee:
			create_response(406, "Employee not found for the current user.")
			return
		sales_person_botique = frappe.get_value("Sales Person", {"employee": employee}, "custom_botique")
		user_data = frappe.db.sql("""
		select u.full_name, u.email, IFNULL(u.mobile_no, '') as mobile_no
		from`tabUser` u
		where u.name = %(user)s
		""",{'user':user},as_dict=1)
		user_data[0]['botique'] = sales_person_botique

		create_response(200, "User Details Fetched!", user_data)
		return
	except Exception as e:
		create_response(406, "No Records Found For User!", e)
		return	