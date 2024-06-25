import frappe
from crm_application_plugin.api.utils import create_response
from functools import reduce

@frappe.whitelist()
def get_home_data():

    site_url = frappe.utils.get_url()
    
    banners = frappe.db.sql("""
    select Concat('{site_url}',slider_image) as file_url from `tabHome page banner mobile`order by idx                       
    """.format(site_url = site_url),as_dict=1)
    
    public_tier = frappe.db.get_all("Client Tiers",filters={"is_public":1},pluck="name")
    customer_counts = frappe.db.sql("""
        SELECT count(c.custom_client_tiers) as no_of_clients, ct.name as tier,ct.tier_index from `tabClient Tiers` ct left join `tabCustomer` c on ct.name = c.custom_client_tiers where (c.custom_sales_person in %(sales_person)s or c.custom_client_tiers in %(public_tiers)s)  group by ct.name
    """,
    {
        "sales_person" : get_sales_person_herarchy(frappe.session.user),
        "public_tiers":public_tier
    },as_dict=1)
    
    client_tiers = [x["tier"] for x in customer_counts]
    if len(client_tiers) > 0:
        condition = " where name not in %(client_tiers)s"
    else:
        condition = ""
    other_tiers = frappe.db.sql(""" select 0 as no_of_clients, name as tier, tier_index from `tabClient Tiers` {condition} """.format(condition=condition),{"client_tiers":client_tiers},as_dict=1)
    customer_counts.extend(other_tiers)
    customer_counts = sorted(customer_counts,key=lambda x : x["tier_index"])
    if customer_counts:
        total = reduce(lambda acc,x : acc + x["no_of_clients"] , customer_counts, 0)

        customer_counts.append({
            "tier" : "Total",
            "no_of_clients" : total
        })

        customer_counts = list(map(lambda x : {
            "tier" : x["tier"],
            "no_of_clients" : x["no_of_clients"],
            "percentage" : 0 if total == 0 else round((x["no_of_clients"] / total) * 100, 2)
        }, customer_counts))
        
    total_count = get_total_count_boutique()
    whatsapp_message = frappe.db.get_single_value("Aetas Whats App Message","whatsapp_message")

    maximum_item_price = frappe.db.sql("""select MAX(shopify_selling_rate) AS max_shopify_selling_rate from`tabItem`""",as_dict=1)
    max_item_price = maximum_item_price[0].max_shopify_selling_rate
     
    create_response(200 , "Home Data Fetched Successfully" , {
        "banners" : banners,
        "overviews" : customer_counts,
        "banner_duration":frappe.db.get_single_value("Aetas CRM Configuration","duration"),
        "total_my_boutique": total_count.get("total_my_boutique", 0),
        "total_other_boutique": total_count.get("total_other_boutique", 0),
        "whatsapp_message":whatsapp_message if whatsapp_message else "",
        "maximum_shopify_selling_rate":max_item_price if max_item_price else 1000000000
    }) 
    
def get_sales_person_herarchy(user,salesperson=None):
    employee = frappe.db.get_value("Employee",{"user_id":user},"name")
    if not employee:
        create_response(406,"Employee not found")
        return
    sales_person = frappe.db.get_value("Sales Person",{"employee":employee},"name")
    if not sales_person:
        create_response(406,"Sales Person not found")
        return
    
    if not salesperson:
        
        sales_person_is_group = frappe.db.get_value("Sales Person",sales_person,"is_group")
        sales_person_list = []
        if sales_person_is_group:
            sales_persons = frappe.db.get_all("Sales Person", filters={"parent_sales_person": sales_person}, pluck="name")
            for person in sales_persons:
                sales_person_list.extend(get_sales_person_herarchy(user, salesperson=person))
        else:
            sales_person_list.append(sales_person)
        
        sales_person_list.append(sales_person)
    else:
        
        sales_person_list = [salesperson]
    
        
    return sales_person_list
    

def get_total_count_boutique():
    try:
        condition = ""
        
        employee = frappe.get_value("Employee", {"user_id": frappe.session.user}, "name")
        if not employee:
            create_response(406, "Employee not found for the current user.")
            return

        boutique_name = frappe.db.get_value("Sales Person", {"employee": employee}, "custom_botique")
        if not boutique_name:
            create_response(406, "Boutique Not Defined For This Sales Person!")
            return

        warehouse_name = frappe.db.get_value("Boutique", boutique_name, 'boutique_warehouse')
        if not warehouse_name:
            create_response(406, "Warehouse Not Defined In Boutique Document!")
            return

        exception_warehouse = [warehouse_name]
        reserverd_warehouse = frappe.db.get_value("Warehouse", warehouse_name, 'custom_reserved_warehouse')
        if reserverd_warehouse:
            exception_warehouse.append(reserverd_warehouse)
        
        total_my_botique = frappe.db.sql("""
        select sum(bn.actual_qty) as total_my_qty from `tabBin` bn inner join `tabItem` it on bn.item_code = it.name where warehouse = %(warehouse)s and it.item_group = 'Watch' group by it.item_group                                  
        """,{"warehouse":warehouse_name},as_dict=1)
        
        total_other_boutique = frappe.db.sql("""
        select sum(bn.actual_qty) as total_other from `tabBin` bn inner join `tabItem` it on bn.item_code = it.name where warehouse not in %(exception_warehouse)s and it.item_group = 'Watch' group by it.item_group
        """,{"exception_warehouse":exception_warehouse},as_dict=1)

        return {
            "total_my_boutique": total_my_botique[0].get("total_my_qty", 0),
            "total_other_boutique": total_other_boutique[0].get("total_other", 0)   
        }
        
    except Exception as e:
        create_response(500, "An error occurred while getting the total count of items", e)
        return
