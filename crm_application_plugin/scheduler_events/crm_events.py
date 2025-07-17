# import frappe
# from frappe.utils import date_diff,add_to_date

# def assign_customer_tier():
#     customer_list = frappe.db.sql("""
#     select name from `tabCustomer`
#     """,as_dict=1)    
#     try:
#         for customer in customer_list:
#             sales_of_customer = get_customer(customer['name'])
#             # print(sales_of_customer)
#             tier = get_applicable_slab(sales_of_customer)
#             # print(tier)
#             frappe.db.set_value("Customer",customer['name'],"custom_client_tiers",tier)
#             set_inactive_customers()
#             frappe.db.commit()
#     except Exception as e:
#         frappe.log_error(message=e, title="Assign Tier Error")
        
# def set_inactive_customers():
#     days = frappe.db.get_single_value("Aetas CRM Configuration", "set_client_tiers_based_on_days")
#     inactive_customers = frappe.db.sql("""
#         SELECT name 
#         FROM `tabCustomer` 
#         WHERE name NOT IN (
#             SELECT customer 
#             FROM `tabSales Invoice` 
#             WHERE docstatus = 1 
#             AND posting_date > %(last_sales_date)s
#         )
#         AND name IN (
#             SELECT customer 
#             FROM `tabSales Invoice` 
#             WHERE docstatus = 1 
#             AND posting_date <= %(last_sales_date)s
#         )
#     """, {
#         "last_sales_date": add_to_date(frappe.utils.today(), days=-days)
#     }, as_list=1)
    
#     inactive_tier_name = frappe.db.get_value("Client Tiers", {"inactive_customer_tier": 1}, "name")
    
#     for customer in inactive_customers:
#         frappe.db.set_value("Customer", customer[0], "custom_client_tiers", inactive_tier_name)

# def get_customer(customer):
#     set_client_tiers_based_on_days = frappe.db.get_single_value("Aetas CRM Configuration", "set_client_tiers_based_on_days")
#     sales_date = add_to_date(frappe.utils.today(),days=-(set_client_tiers_based_on_days or 730))
#     sales_details = frappe.db.sql("""
#     select customer,sum(grand_total) as net_sales from `tabSales Invoice` where docstatus = 1 and customer = %(customer)s and posting_date > %(last_sales_date)s group by customer
#     """,({
#         "customer":customer,
#         "last_sales_date":sales_date
#     }),as_dict=1)
    
#     return sales_details[0]['net_sales'] if sales_details else 0

# def get_applicable_slab(sales):
#     tier_slab = frappe.db.sql("""
#     select tier,min_purchase,max_purchase from `tabClient Tiers` where inactive_customer_tier = 0
#     """,as_dict = 1)

#     for item in tier_slab:
#         if sales >= item['min_purchase'] and sales <= item['max_purchase']:
#             print(item['tier'])
#             return item['tier']

#     return None

import frappe
from frappe.utils import add_to_date, now

def sync_customer_tiers_scheduler():
    try:
        last_sync = frappe.db.get_single_value("Aetas CRM Configuration", "last_customer_tier_sync")
        batch_size = 1000

        if not last_sync:
            frappe.log_error("Running full customer tier sync for the first time.", "Customer Tier Sync Info")
            all_customers = frappe.db.get_all("Customer", pluck="name")
            for i in range(0, len(all_customers), batch_size):
                batch = all_customers[i:i + batch_size]
                frappe.enqueue(
                    "crm_application_plugin.scheduler_events.crm_events.assign_customer_tier_batch",
                    customers=batch,
                    queue="long",
                    now=False
                )
        else:
            # Subsequent runs: sync only customers with updated invoices
            updated_customers = frappe.db.sql("""
                SELECT DISTINCT customer 
                FROM `tabSales Invoice` 
                WHERE docstatus = 1 AND modified > %(last_sync)s
            """, {
                "last_sync": last_sync
            }, as_list=1)

            updated_customers = [c[0] for c in updated_customers]

            if not updated_customers:
                frappe.log_error("No customers with updated invoices found since last sync.", "Customer Tier Sync Info")
                frappe.db.set_value("Aetas CRM Configuration", None, "last_customer_tier_sync", now())
                return
            
            for i in range(0, len(updated_customers), batch_size):
                batch = updated_customers[i:i + batch_size]
                frappe.enqueue(
                    "crm_application_plugin.scheduler_events.crm_events.assign_customer_tier_batch",
                    customers=batch,
                    queue="long",
                    now=False
                )

        # ✅ Always update sync time
        frappe.db.set_value("Aetas CRM Configuration", None, "last_customer_tier_sync", now())

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Customer Tier Sync Scheduler Error")


def assign_customer_tier_batch(customers: list):
    try:
        for customer in customers:
            sales = get_customer_sales(customer)
            tier = get_applicable_slab(sales)
            if tier:
                frappe.db.set_value("Customer", customer, "custom_client_tiers", tier)

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="Assign Tier Batch Error")

def get_customer_sales(customer):
    days = frappe.db.get_single_value("Aetas CRM Configuration", "set_client_tiers_based_on_days") or 730
    from_date = add_to_date(frappe.utils.today(), days=-days)

    result = frappe.db.sql("""
        SELECT SUM(grand_total) as net_sales 
        FROM `tabSales Invoice` 
        WHERE docstatus = 1 AND customer = %(customer)s AND posting_date > %(from_date)s
    """, {
        "customer": customer,
        "from_date": from_date
    }, as_dict=True)

    return result[0]['net_sales'] or 0 if result else 0

def get_applicable_slab(sales):
    slabs = frappe.db.sql("""
        SELECT tier, min_purchase, max_purchase 
        FROM `tabClient Tiers` 
        WHERE inactive_customer_tier = 0
    """, as_dict=True)

    for slab in slabs:
        if slab['min_purchase'] <= sales <= slab['max_purchase']:
            return slab['tier']
    return None

def set_inactive_customers():
    try:
        days = frappe.db.get_single_value("Aetas CRM Configuration", "set_client_tiers_based_on_days") or 730
        last_sales_date = add_to_date(frappe.utils.today(), days=-days)

        inactive_customers = frappe.db.sql("""
            SELECT name 
            FROM `tabCustomer` 
            WHERE name NOT IN (
                SELECT DISTINCT customer 
                FROM `tabSales Invoice` 
                WHERE docstatus = 1 AND posting_date > %(last_sales_date)s
            )
            AND EXISTS (
                SELECT 1 
                FROM `tabSales Invoice` 
                WHERE customer = `tabCustomer`.name 
                AND docstatus = 1 
                AND posting_date <= %(last_sales_date)s
            )
        """, {
            "last_sales_date": last_sales_date
        }, as_list=1)

        customer_names = [c[0] for c in inactive_customers]
        batch_size = 200

        for i in range(0, len(customer_names), batch_size):
            batch = customer_names[i:i + batch_size]
            frappe.enqueue(
                "crm_application_plugin.scheduler_events.crm_events.set_inactive_customers_batch",
                customers=batch,
                queue="long",
                now=False
            )
    except Exception as e:
        frappe.log_error("Set Inactive Customer Issue",frappe.get_traceback())




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
