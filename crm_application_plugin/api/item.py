import frappe
from crm_application_plugin.api.utils import create_response
from functools import reduce


@frappe.whitelist()
def get_product_list():
    try:
        search = frappe.local.form_dict.search or ""
        offset = int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0

        condition = ("")
        if search is not None and search != "":
            condition += "Where i.item_name like %(search)s or i.item_code like %(search)s"
               
        
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            create_response(404, "Employee not found for the current user.")
            return

        boutique_name = frappe.get_value("Sales Person", {"employee": employee}, "custom_botique")
        if not boutique_name:
            create_response(404, "Boutique Not Define For This Sales Person!")
            return
        
        warehouse_name = frappe.db.get_value("Boutique",boutique_name,'boutique_warehouse')
        if not warehouse_name:
            create_response(404, "Warehouse Not Define In Boutique Document!")
            return

        price_list = frappe.db.get_value("Aetas CRM Configuration",None,'default_price_list')
        if not price_list:
            create_response(404, "Default price list is not defined in the settings!")
            return

        item_details = frappe.db.sql("""
            SELECT i.item_code, i.item_name, IFNULL(i.image,'') as image, IFNULL(ip.price_list_rate, 0) as price,(select IFNULL(actual_qty,0) from `tabBin` where item_code = i.item_code and warehouse = %(warehouse)s) as my_boutique,(select IFNULL(sum(actual_qty),0) from `tabBin` where item_code = i.item_code and warehouse != %(warehouse)s group by item_code) as other_boutique
            FROM `tabItem` i
            LEFT JOIN `tabItem Price` ip ON i.item_code = ip.item_code AND ip.price_list = %(price_list)s
            {conditions} 
            GROUP BY i.item_code
            LIMIT %(offset)s,20
            """.format(conditions = condition),{
                "search" : "%"+search+"%",
                "offset" : int(offset),
                "price_list":price_list,
                "warehouse":warehouse_name
        },as_dict=1)

        create_response(200, "Item data Fetched Successfully!", item_details)
        return
    except Exception as e:
        create_response(500,"An error occurred while getting list of item",e)
        return   


@frappe.whitelist()
def get_product_detail(item_code):
    # Get details of product baesd on parameter
    try:
        
        item_details = frappe.db.sql("""
        select i.item_name,i.description,i.custom_reference,i.custom_collection,i.custom_dial_size,i.custom_dial_shape,i.custom_case_material,
        i.custom_diamonds,i.custom_strap_bracelet,i.custom_gender,i.custom_movement,i.custom_water_resistance,i.custom_brand_warranty, i.brand,
        f.file_url, (SELECT b.custom_brand_logo FROM `tabBrand` b WHERE b.name = i.brand) AS brand_logo
        from`tabItem` i
        left join`tabFile` f on i.name = f.attached_to_name
        where f.attached_to_doctype = "Item" and i.name = %(item_code)s
        """,{'item_code':item_code},as_dict=1)

        item_price = frappe.db.get_value("Item Price",{'item_code':item_code},'price_list_rate')
        # url = frappe.utils.get_url()

        if item_details:
            item_info = {
                'item_name':item_details[0]["item_name"] or '',
                'description':item_details[0]["description"] or '',
                'reference': item_details[0]["custom_reference"] or '',
                'collection': item_details[0]["custom_collection"] or '',
                'dial_size': item_details[0]["custom_dial_size"] or '',
                'dial_shape': item_details[0]["custom_dial_shape"] or '',
                'case_material': item_details[0]["custom_case_material"] or '',
                'diamonds': item_details[0]["custom_diamonds"] or '',
                'strap_bracelet': item_details[0]["custom_strap_bracelet"] or '',
                'gender': item_details[0]["custom_gender"] or '',
                'movement': item_details[0]["custom_movement"] or '',
                'water_resistance': item_details[0]["custom_water_resistance"] or '',
                'brand_warranty': item_details[0]["custom_brand_warranty"] or '',
                'brand_logo': item_details[0]["brand_logo"] or '',
                'brand': item_details[0]["brand"] or '',
                'price': item_price or 0.0,
                'images': [image['file_url'] for image in item_details if image.get('file_url')]
                # 'image_info': [{'image_url': url + image['file_url']} for image in item_details if image.get('file_url')]
            }
           

        create_response(200, "Item data Fetched Successfully!", item_info if item_details else {})
        return 
    except Exception as e:
        create_response(500,"An error occurred while getting data of item",e)
        return   

@frappe.whitelist()
def brand_list():
    #get list of brand
    try:
        
        brand_details = frappe.db.sql("""
            SELECT
                b.name AS brand_name,
                f.file_url,
                IFNULL(bp.title, '') AS pdf_title,
                IFNULL(bv.title, '') AS video_title
            FROM `tabBrand` b
            LEFT JOIN `tabFile` f ON b.name = f.attached_to_name
            LEFT JOIN `tabBrand Pdfs` bp ON b.name = bp.parent
            LEFT JOIN `tabBrand Videos` bv ON b.name = bv.parent
            WHERE f.attached_to_doctype = 'Brand'
        """, as_dict=1)
        
        # Organize the data into a structured format
        brand_info = reduce(training_subjects, brand_details ,{})
        brand_info = list(map(lambda x : {
            "name" : x["brand_name"],
            "file_url" : x["file_url"],
            "subjects" : list(x["subjects"])
        },brand_info.values()))
       
        create_response(200, "Brand List Fetched Successfully!", brand_info)
        return 
    except Exception as e:
        create_response(500,"An error occurred while getting brand list",e)
        return   
    
    
def training_subjects(acc , data):
    brand = data["brand_name"]
    if brand not in acc:
        acc[brand] = {
            'brand_name': brand,
            'file_url': data['file_url'],
            'subjects': set(),
        }
    
    if data["pdf_title"]:
        acc[brand]["subjects"].add(data["pdf_title"])
    
    if data["video_title"]:
        acc[brand]["subjects"].add(data["video_title"])
    
    return acc
               
@frappe.whitelist()
def stock_list_other_botique(item):
    try:
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            create_response(404, "Employee not found for the current user.")
            return

        boutique_name = frappe.get_value("Sales Person", {"employee": employee}, "custom_botique")
        if not boutique_name:
            create_response(404, "Boutique Not Define For This Sales Person!")
            return
        
        warehouse_name = frappe.db.get_value("Boutique",boutique_name,'boutique_warehouse')
        if not warehouse_name:
            create_response(404, "Warehouse not define in boutique document!")
            return
        
        item_details = frappe.db.sql("""
                SELECT i.item_code, i.item_name, IFNULL(i.image,'') as image,bn.actual_qty,bn.warehouse
                FROM `tabItem` i
                LEFT JOIN `tabBin` bn ON i.item_code = bn.item_code 
                Where bn.warehouse != %(warehouse)s and i.item_code = %(item_code)s
                
                """,{
                    "warehouse":warehouse_name,
                    "item_code":item
            },as_dict=1)
        
        
        create_response(200, "Stock of item from other warehouses fetched successfully!", item_details)
        return
    except Exception as e:
        create_response(406, "Something went Wrong!", frappe.get_traceback())
        return
        