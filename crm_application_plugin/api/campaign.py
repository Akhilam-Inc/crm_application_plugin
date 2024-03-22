import frappe
from crm_application_plugin.api.utils import create_response



@frappe.whitelist()
def create_campaign(campaign_name,start_date,end_date):
    try:
        if not campaign_name or not start_date or not end_date:
            return create_response(422, "Invalid request data", "Please provide campaign_name, start_date, and end_date.")
            
        cam_obj = frappe.new_doc("Campaign")
        cam_obj.campaign_name = campaign_name
        cam_obj.custom_start_date = start_date
        cam_obj.custom_end_date = end_date 
        cam_doc = cam_obj.insert(ignore_permissions= 1)
        create_response(200,"Campaign created successfully",cam_doc.name)
    except Exception as e:
        create_response(406,"Campaign creation failed",frappe.get_traceback())  

@frappe.whitelist()
def campaign_list():
    campaign_list = frappe.db.sql("""
    select count(td.custom_customer) as customer_count,cp.name as campaign,cp.custom_start_date,cp.custom_end_date,cp.description from `tabToDo` td inner join `tabCampaign` cp on td.reference_name = cp.name where cp.custom_enable = 1 group by cp.name        
    """,as_dict=1)

    create_response(200,"List of Campaign fetched successfully",campaign_list)

@frappe.whitelist()
def boutique_list():
    # Get List of Botique
    search = frappe.local.form_dict.search or ""
    offset = int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0
    
    condition = ("")
    if search is not None and search != "":
        condition += "where boutique_name like %(search)s"
               
    
    boutique_names = frappe.db.sql("""
    select IFNULL(boutique_name,'') as boutique_name ,IFNULL(boutique_address,'') as boutique_address,IFNULL(boutique_phone_no,'') as boutique_phone,
    IFNULL(boutique_email_id,'') as boutique_email_id from`tabBoutique`{conditions} LIMIT %(offset)s,20 """.format(conditions = condition),{
            "search" : "%" + search + "%",
            "offset" : offset
        },as_dict=1)

    create_response(200,"List of Boutique fetched successfully",boutique_names)
