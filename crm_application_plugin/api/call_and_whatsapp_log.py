import frappe
from crm_application_plugin.api.utils import create_response


@frappe.whitelist()
def create_call_log(call_by,call_to,mobile_no):
	try:
		if not call_by or not call_to or not mobile_no:
			create_response(400, "Invalid request data", "Please provide call_by, call_to, and mobile_no.")
			return 
		
		call_obj = frappe.new_doc("Aetas Call Log")
		call_obj.call_by = call_by
		call_obj.call_to = call_to
		call_obj.call_initiated_at = frappe.utils.now() 
		call_obj.mobile_number = mobile_no
		call_doc = call_obj.insert(ignore_permissions= 1)

		create_response(200,"Aetas Call Log created successfully",call_doc.name)
		return
		
	except Exception as e:
		create_response(406,"Aetas Call Log creation failed",frappe.get_traceback()) 
		return   


@frappe.whitelist()
def create_whatsapp_log(message_by,message_to,mobile_no,message):
	try:
		if not message_by or not message_to or not mobile_no:
			create_response(400, "Invalid request data", "Please provide message_by, message_to, and mobile_no.")
			return 
		
		whatsapp_obj = frappe.new_doc("Aetas WhatsApp Log")
		whatsapp_obj.message_by = message_by
		whatsapp_obj.message_to = message_to
		whatsapp_obj.sent_on = frappe.utils.now()
		whatsapp_obj.mobile_number = mobile_no
		whatsapp_obj.message = message
		whatsapp_doc = whatsapp_obj.insert(ignore_permissions= 1)

		create_response(200,"Aetas Call Log created successfully",whatsapp_doc.name)
		return

	except Exception as e:
		create_response(406,"Aetas Call Log creation failed",frappe.get_traceback()) 
		return