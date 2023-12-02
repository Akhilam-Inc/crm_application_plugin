import frappe
from crm_application_plugin.api.utils import create_response
from functools import reduce

@frappe.whitelist()
def get_home_data():

    site_url = frappe.utils.get_url()
    
    banners = frappe.db.sql("""
    select Concat('{site_url}',slider_image) as file_url from `tabHome page banner mobile`order by idx                       
    """.format(site_url = site_url),as_dict=1)
    

    customer_counts = frappe.db.sql("""
        SELECT count(c.custom_client_tiers) as no_of_clients, ct.name as tier from `tabClient Tiers` ct left join `tabCustomer` c on ct.name = c.custom_client_tiers where c.custom_sales_person in %(sales_person)s group by ct.name
    """,
    {
        "sales_person" : get_sales_person_herarchy(frappe.session.user)
    },as_dict=1)

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
     
    create_response(200 , "Home Data Fetched Successfully" , {
        "banners" : banners,
        "overviews" : customer_counts,
        "banner_duration":frappe.db.get_single_value("Aetas CRM Configuration","duration")
    }) 
    
def get_sales_person_herarchy(user):
    employee = frappe.db.get_value("Employee",{"user_id":user},"name")
    if not employee:
        create_response(406,"Employee not found")
        return
    sales_person = frappe.db.get_value("Sales Person",{"employee":employee},"name")
    if not sales_person:
        create_response(406,"Sales Person not found")
        return
    
    sales_person_is_group = frappe.db.get_value("Sales Person",sales_person,"is_group")
    sales_person_list = []
    if sales_person_is_group:
        sales_persons = frappe.db.get_all("Sales Person",{"parent_sales_person":sales_person},["name"],pluck="name")
        sales_person_list = sales_persons
    
    sales_person_list.append(sales_person)
        
    return sales_person_list
    
    

    
