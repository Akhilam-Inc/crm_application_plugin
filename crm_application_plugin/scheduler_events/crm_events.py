import frappe
from frappe.utils import date_diff,add_to_date

def assign_customer_tier():
    customer_list = frappe.db.sql("""
    select name from `tabCustomer`
    """,as_dict=1)    

    for customer in customer_list:
        sales_of_customer = get_customer(customer['name'])
        tier = get_applicable_slab(sales_of_customer)
        print(tier)
        frappe.db.set_value("Customer",customer['name'],"custom_client_tiers",tier)
        frappe.db.commit()


def get_customer(customer):
    sales_date = add_to_date(frappe.utils.today(), years=-2)
    print(sales_date)
    sales_details = frappe.db.sql("""
    select customer,sum(grand_total) as net_sales from `tabSales Invoice` where docstatus = 1 and customer = %(customer)s and posting_date > %(last_sales_date)s group by customer
    """,({
        "customer":customer,
        "last_sales_date":sales_date
    }),as_dict=1)
    print(sales_details)
    return sales_details[0]['net_sales'] if sales_details else 0

def get_applicable_slab(sales):
    tier_slab = frappe.db.sql("""
    select tier,min_purchase,max_purchase from `tabClient Tiers` 
    """,as_dict = 1)

    for item in tier_slab:
        if sales > item['min_purchase'] and sales < item['max_purchase']:
            print(item['tier'])
            return item['tier']

    return None