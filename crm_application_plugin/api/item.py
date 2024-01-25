import frappe
from crm_application_plugin.api.utils import create_response
from functools import reduce
from shopify.resources import Product, Variant
import frappe
from crm_application_plugin.api.utils import create_response
from functools import reduce
from shopify.resources import Product, Variant
import requests
from requests.exceptions import RequestException


@frappe.whitelist()
def get_product_list():
    
    try:
        search = frappe.local.form_dict.search or ""
        offset = int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0

        condition = ("")
        if search is not None and search != "":
            condition += "and (i.item_name like %(search)s or i.item_code like %(search)s)"
               
        
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            create_response(406, "Employee not found for the current user.")
            return

        boutique_name = frappe.get_value("Sales Person", {"employee": employee}, "custom_botique")
        if not boutique_name:
            create_response(406, "Boutique Not Define For This Sales Person!")
            return
        
        warehouse_name = frappe.db.get_value("Boutique",boutique_name,'boutique_warehouse')
        if not warehouse_name:
            create_response(406, "Warehouse Not Define In Boutique Document!")
            return
        
        if frappe.local.form_dict.myboutique:
            having_condition = "HAVING my_boutique > 0"
        else:
            having_condition = ""
        
        reserverd_warehouse = frappe.db.get_value("Warehouse",warehouse_name,'custom_reserved_warehouse')
        
        exception_warehouse = [warehouse_name,reserverd_warehouse]


        item_details = frappe.db.sql("""
            SELECT i.item_code, i.item_name, IFNULL(i.image,'') as image, i.shopify_selling_rate as price,
            (select IFNULL(actual_qty,0) from `tabBin` where item_code = i.item_code and warehouse = %(warehouse)s) as my_boutique,
            (select IFNULL(actual_qty,0) from `tabBin` where item_code = i.item_code and warehouse = %(reserved_warehouse)s) as my_reserved,
            (select IFNULL(sum(actual_qty),0) from `tabBin` where item_code = i.item_code and warehouse not in %(exception_warehouse)s) as other_boutique,
            CONCAT('https://artoftimeindia.com/products/', i.product_handle) as share_link
            FROM `tabItem` i
            where i.item_group = 'Watch' and i.product_handle is not null
            {conditions} 
            GROUP BY i.item_code {having_condition}
            LIMIT %(offset)s,20
            """.format(conditions = condition,having_condition=having_condition),{
                "search" : "%"+search+"%",
                "offset" : int(offset),
                "warehouse":warehouse_name,
                "reserved_warehouse":reserverd_warehouse,
                "exception_warehouse":exception_warehouse
        },as_dict=1)
        
        

        create_response(200, "Item data Fetched Successfully!", item_details)
        return
    except Exception as e:
        create_response(500,"An error occurred while getting list of item",e)
        return   


@frappe.whitelist()
def get_product_detail(item_code):
    # Get details of product based on parameter
    ecommerce_item_code = frappe.db.get_value("Ecommerce Item", {"erpnext_item_code": item_code}, "integration_item_code")
    if not ecommerce_item_code:
        create_response(406, "Ecommerce Item Not Found!")
        return
    try:
        product_details = get_product_details_from_shopify(ecommerce_item_code)
        if not product_details:
            create_response(406, "Product Not Found!")
            return
        product_meta = get_product_details_from_shopify(ecommerce_item_code, 1)
        if not product_meta:
            create_response(406, "Product Meta Not Found!")
            return

        item_info = {
            'item_name': product_details["product"]["title"],
            'description': product_details["product"]["body_html"],
            'reference': get_metafield_value(product_meta, "reference"),
            'collection': get_metafield_value(product_meta, "collection"),
            'dial_size': get_metafield_value(product_meta, "dial_size"),
            'dial_shape': get_metafield_value(product_meta, "dial_shape"),
            'case_material': get_metafield_value(product_meta, "case_material"),
            'diamonds': get_metafield_value(product_meta, "diamonds"),
            'strap_bracelet': get_metafield_value(product_meta, "strap_bracelet"),
            'gender': get_metafield_value(product_meta, "gender"),
            'movement': get_metafield_value(product_meta, "movement"),
            'water_resistance': get_metafield_value(product_meta, "water_resistance"),
            'brand_warranty': get_metafield_value(product_meta, "warranty"),
            'brand_logo': '',
            'brand': get_metafield_value(product_meta, "brand"),
             'price' : float(product_details["product"]["variants"][0]["price"]),
            'images': [image['src'] for image in product_details["product"]["images"]],
            'share_link': "https://artoftimeindia.com/products/"+product_details["product"]["handle"],
        }

        create_response(200, "Item data Fetched Successfully!", item_info)
        return 
    except Exception as e:
        create_response(500, "An error occurred while getting data of item", e)
        return   

def get_metafield_value(product_meta, key):
    for metafield in product_meta["metafields"]:
        if metafield["key"] == key:
            return metafield["value"]
    return ''




def get_product_details_from_shopify(item,meta=0):
    try:
        shopify_settings = frappe.get_single("Shopify Setting")
        secret = shopify_settings.get_password("password")
        if not meta:
            url = "https://"+shopify_settings.shopify_url+"/admin/api/2023-07/products/{product_id}.json".format(product_id=item)
        else:
            url = "https://"+shopify_settings.shopify_url+"/admin/api/2023-10/products/{product_id}/metafields.json".format(product_id=item)
        headers = {
            "X-Shopify-Access-Token":secret
        }
        res= get_request(url, headers)
        return res
    except Exception as e:
        if not meta:
            frappe.log_error(title="Shoppify Product get call",message=e)
        else:
            frappe.log_error(title="Shoppify Product metafield get call",message=e)
        return None
    


def get_request(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

    except RequestException as err:
        frappe.log_error(title="Shoppify Product get call",message=err)
        return None

    except Exception as err:
        frappe.log_error(title="Shoppify Product get call",message=err)
        return None

    return response.json()
    
    

@frappe.whitelist()
def brand_list():
    #get list of brand
    try:
        
        brand_details = frappe.db.sql("""
            SELECT
                b.name AS brand_name,
                b.custom_brand_logo as file_url,
                IFNULL(bp.title, '') AS pdf_title,
                IFNULL(bv.title, '') AS video_title
            FROM `tabBrand` b
            LEFT JOIN `tabBrand Pdfs` bp ON b.name = bp.parent
            LEFT JOIN `tabBrand Videos` bv ON b.name = bv.parent
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
        create_response(409,"An error occurred while getting brand list",e)
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
            create_response(406, "Employee not found for the current user.")
            return

        boutique_name = frappe.get_value("Sales Person", {"employee": employee}, "custom_botique")
        if not boutique_name:
            create_response(406, "Boutique Not Define For This Sales Person!")
            return
        
        warehouse_name = frappe.db.get_value("Boutique",boutique_name,'boutique_warehouse')
        if not warehouse_name:
            create_response(406, "Warehouse not define in boutique document!")
            return
        
        item_details = frappe.db.sql("""
                SELECT i.item_code, i.item_name, IFNULL(i.image,'') as image,bn.actual_qty,bn.warehouse
                FROM `tabItem` i
                LEFT JOIN `tabBin` bn ON i.item_code = bn.item_code 
                inner join `tabWarehouse` wh on wh.name = bn.warehouse
                Where bn.warehouse != %(warehouse)s and i.item_code = %(item_code)s and wh.custom_is_reserved = 0
                
                """,{
                    "warehouse":warehouse_name,
                    "item_code":item
            },as_dict=1)
        
        
        create_response(200, "Stock of item from other warehouses fetched successfully!", item_details)
        return
    except Exception as e:
        create_response(406, "Something went Wrong!", frappe.get_traceback())
        return
    

        
        
    
        