import frappe
from crm_application_plugin.api.utils import create_response



@frappe.whitelist()
def create_campaign(campaign_name,start_date,end_date):
    try:
        if not campaign_name or not start_date or not end_date:
            return create_response(400, "Invalid request data", "Please provide campaign_name, start_date, and end_date.")
            
        cam_obj = frappe.new_doc("Campaign")
        cam_obj.campaign_name = campaign_name
        cam_obj.custom_start_date = start_date
        cam_obj.custom_end_date = end_date 
        cam_doc = cam_obj.insert(ignore_permissions= 1)
        create_response(200,"Campaign created successfully",cam_doc.name)
    except Exception as e:
        create_response(406,"Campaign creation failed",frappe.get_traceback())  