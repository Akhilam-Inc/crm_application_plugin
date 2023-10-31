import frappe
from crm_application_plugin.api.utils import create_response

@frappe.whitelist()
def get_user_details():
	try:
		user = frappe.session.user
		user_data = frappe.db.sql("""
		select u.full_name, u.email, IFNULL(u.mobile_no, '') as mobile_no
		from`tabUser` u
		where u.name = %(user)s
		""",{'user':user},as_dict=1)

		create_response(200, "Assigned Customer List Fetched!", user_data)
		return
	except Exception as e:
		create_response(406, "No Records Found For User!", e)
		return	