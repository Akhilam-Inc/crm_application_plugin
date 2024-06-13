import frappe
from crm_application_plugin.api.utils import create_response


@frappe.whitelist()
def brand_training_list(brand, subject, type):

    if type == "training":
        # Check for missing mandatory fields
        if not brand or not subject:
            return create_response(422, "Invalid request data", "Please provide all mandatory field data.")

        try:
            # Use frappe.db.sql to fetch data
            brand_training_details = frappe.db.sql("""
            SELECT
                bt.brand,
                bp.title,
                bp.attach,
                bv.title AS video_title,
                bv.file_url
            FROM `tabBrand Training` bt
            LEFT JOIN `tabBrand Pdfs` bp ON bt.name = bp.parent
            LEFT JOIN `tabBrand Videos` bv ON bt.name = bv.parent
            WHERE bt.name = %(brand)s AND bp.title = %(subject)s
            """, {'brand': brand, 'subject': subject}, as_dict=1)

            brand_info = {
                'brand_name': brand,
                'pdfs':  list(map(lambda x : {
                        "name" : x["title"] or "",
                        "file" : x["attach"] or ""
                    } , brand_training_details)),
                'videos': list(map(lambda x : {
                        "name" : x["video_title"] or "",
                        "file" : x["file_url"] or ""
                    } , brand_training_details)),
            }
            create_response(200, "Brand training details fetched successfully.", brand_info)
            return
        except Exception as e:
            frappe.log_error(message=str(e), title="Error in brand training records")
            create_response(406, "Internal Server Error", "An error occurred while processing your request.")
            return
    else:
        try:
            brand_info = {
                'brand_name': "",
                'pdfs': [],
                'videos': []
            }
            brand_pdfs = frappe.db.sql("""
            select bp.title as name, bp.attach as file
            from `tabBrand Pdfs` bp where bp.parent = "User Guide" order by name
            """,as_dict=1)

            brand_info['pdfs'] = brand_pdfs or []
            
            brand_videos = frappe.db.sql("""
            select bv.title as name,IFNULL(bv.file_url,'') as file
            from`tabBrand Videos` bv where bv.parent = "User Guide" order by name
            """,as_dict=1)
            
            brand_info['videos'] = brand_videos or []
            brand_info['brand_name'] = "User Guide"

            create_response(200, "User Guide Details fetched successfully.", brand_info)
            return
            
        except Exception as e:
            frappe.log_error(message=str(e), title="Error in user guide records")
            create_response(406, "Something Went Wrong", "An error occurred while processing your request.")
            return
        


