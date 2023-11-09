import frappe
from crm_application_plugin.api.utils import create_response
from functools import reduce

@frappe.whitelist()
def get_home_data():

    banners = []

    customer_counts = frappe.db.sql("""
        SELECT count(c.custom_client_tiers) as no_of_clients, ct.name as tier from `tabClient Tiers` ct left join `tabCustomer` c on ct.name = c.custom_client_tiers group by ct.name
    """, as_dict = 1)

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
        "overviews" : customer_counts
    })    
    
