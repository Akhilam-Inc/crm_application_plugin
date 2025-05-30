import frappe
from frappe.utils import date_diff,add_to_date

def assign_customer_tier():
    customer_list = frappe.db.sql("""
    select name from `tabCustomer`
    """,as_dict=1)    
    try:
        for customer in customer_list:
            sales_of_customer = get_customer(customer['name'])
            # print(sales_of_customer)
            tier = get_applicable_slab(sales_of_customer)
            # print(tier)
            frappe.db.set_value("Customer",customer['name'],"custom_client_tiers",tier)
            set_inactive_customers()
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(message=e, title="Assign Tier Error")
        
def set_inactive_customers():
    days = frappe.db.get_single_value("Aetas CRM Configuration", "set_client_tiers_based_on_days")
    inactive_customers = frappe.db.sql("""
        SELECT name 
        FROM `tabCustomer` 
        WHERE name NOT IN (
            SELECT customer 
            FROM `tabSales Invoice` 
            WHERE docstatus = 1 
            AND posting_date > %(last_sales_date)s
        )
        AND name IN (
            SELECT customer 
            FROM `tabSales Invoice` 
            WHERE docstatus = 1 
            AND posting_date <= %(last_sales_date)s
        )
    """, {
        "last_sales_date": add_to_date(frappe.utils.today(), days=-days)
    }, as_list=1)
    
    inactive_tier_name = frappe.db.get_value("Client Tiers", {"inactive_customer_tier": 1}, "name")
    
    for customer in inactive_customers:
        frappe.db.set_value("Customer", customer[0], "custom_client_tiers", inactive_tier_name)

def get_customer(customer):
    set_client_tiers_based_on_days = frappe.db.get_single_value("Aetas CRM Configuration", "set_client_tiers_based_on_days")
    sales_date = add_to_date(frappe.utils.today(),days=-(set_client_tiers_based_on_days or 730))
    sales_details = frappe.db.sql("""
    select customer,sum(grand_total) as net_sales from `tabSales Invoice` where docstatus = 1 and customer = %(customer)s and posting_date > %(last_sales_date)s group by customer
    """,({
        "customer":customer,
        "last_sales_date":sales_date
    }),as_dict=1)
    
    return sales_details[0]['net_sales'] if sales_details else 0

def get_applicable_slab(sales):
    tier_slab = frappe.db.sql("""
    select tier,min_purchase,max_purchase from `tabClient Tiers` where inactive_customer_tier = 0
    """,as_dict = 1)

    for item in tier_slab:
        if sales >= item['min_purchase'] and sales <= item['max_purchase']:
            print(item['tier'])
            return item['tier']

    return None


def assign_sales_person():
    sales_person_sales_data = frappe.db.sql("""
    select 
    si.customer,si.posting_date,sum(sii.amount) as total,sii.sales_person 
    from `tabSales Invoice` si inner join `tabSales Invoice Item` sii on si.name = sii.parent 
    where sii.sales_person is not null and si.docstatus = 1 
    group by si.customer,sii.sales_person 
    order by si.posting_date desc
    """,as_dict = 1)

    output = map_customer_to_salesperson_optimized(sales_person_sales_data)
    
    
    for customer, sales_person in output.items():
        is_enabled= frappe.db.get_value("Sales Person", sales_person, "enabled")
        if is_enabled:
            frappe.db.set_value("Customer",customer,"custom_sales_person",sales_person)
        
    
    frappe.db.commit()
    

def map_customer_to_salesperson_optimized(sales_data):
    # Dictionary to hold the best sales record for each customer
    customer_sales_map = {}

    for record in sales_data:
        customer = record['customer']
        sales_info = (record['total'], record['posting_date'], record['sales_person'])

        # Update the record if it's either the first one, or a better one
        if customer not in customer_sales_map or sales_info > customer_sales_map[customer]:
            customer_sales_map[customer] = sales_info

    # Construct the final mapping of customer to salesperson
    return {customer: sales_info[2] for customer, sales_info in customer_sales_map.items()}
