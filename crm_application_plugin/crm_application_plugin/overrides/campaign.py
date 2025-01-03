import frappe
import json
from frappe.utils import today,cint, getdate

@frappe.whitelist()
def create_todo(self):
    try:
        self = json.loads(self)
        todo_created = False
        
        for item in self['custom_customer_campaign_list_']:
            employee = frappe.db.get_value('Sales Person', item['sales_person'], 'employee')
            user_id = frappe.db.get_value('Employee', employee, 'user_id')

            if not user_id or not employee:
                frappe.msgprint("Sales Person Employee Mapping isn't Correctly Done For Your User: <b>{0}</b>. Kindly Contact Admin!".format(item['sales_person']))
                continue

            if not frappe.db.exists("ToDo", {'reference_name': self['name'], 'custom_customer': item['customer_name']}):
                todo = frappe.new_doc("ToDo")
                todo.description = self['description']
                todo.status = 'Open'
                todo.priority = 'High'
                todo.allocated_to = user_id
                todo.date = frappe.utils.today()
                todo.custom_customer = item['customer_name']
                todo.reference_type = 'Campaign'
                todo.reference_name = self['name']

                todo.insert(ignore_permissions=1)
                todo_created = True
        if todo_created:
            frappe.msgprint("Todos Created For Sales Person.")
    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="ToDo Creation Failed")
        frappe.msgprint("An Error Occurred while Creating ToDo From Campaign!")

@frappe.whitelist()
def get_customer_by_tiers(client_tier,sales_person):
    client_list = frappe.db.sql("""
    select name,custom_sales_person,custom_client_tiers from `tabCustomer` where custom_client_tiers = %(tiers)s and custom_sales_person = %(sales_person)s   
    """,({
        'tiers' : client_tier,
        'sales_person':sales_person
    }),as_dict = 1)

    return client_list

# @frappe.whitelist()
# def get_sales_details(days, date = None):

#     if date is None:
#         date = getdate(today())
    
#     print(date)

#     return frappe.db.sql(
#         """SELECT
#             cust.name,
#             cust.custom_client_tiers,
#             cust.custom_sales_person,
#             max(so.posting_date) as 'last_order_date',
#             DATEDIFF(%(date)s, max(so.posting_date)) as 'days_since_last_order'
#         FROM `tabCustomer` cust
#            LEFT JOIN `tabSales Invoice` so ON cust.name = so.customer
#         WHERE 
#             so.docstatus = 1
#         GROUP BY so.customer
#         HAVING days_since_last_order >= {days}
#         ORDER BY days_since_last_order DESC""".format(
#         days = days),{
#             "date" : date
#         },
#         as_dict=1
#     )

@frappe.whitelist()
def get_sales_details(from_date,to_date):

    data = frappe.db.sql(
        """SELECT
            cust.name,
            cust.custom_client_tiers,
            cust.custom_sales_person,
            max(so.posting_date) as last_order_date
        FROM `tabCustomer` cust
        LEFT JOIN `tabSales Invoice` so ON cust.name = so.customer
        WHERE 
            so.docstatus = 1
            AND so.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY so.customer
        """,
        {
            "from_date": from_date,
            "to_date": to_date
        },
        as_dict=1
    )
    if not data:
        frappe.throw("No data found for the specified criteria")
    return data

# @frappe.whitelist()
# def get_last_contacted(day):
#     return  frappe.db.sql("""
#     SELECT c.name,c.custom_sales_person,c.custom_client_tiers
#     FROM `tabCustomer` c
#     LEFT JOIN (
#         SELECT customer, MAX(contacted_date) AS last_contacted
#         FROM (
#             SELECT message_to as customer, sent_on as contacted_date FROM `tabAetas WhatsApp Log`
#             UNION ALL
#             SELECT call_to as customer, call_initiated_at as contacted_date FROM `tabAetas Call Log`
#         ) AS combined_logs
#         GROUP BY customer
#     ) AS contact_logs ON c.name = contact_logs.customer
#     WHERE contact_logs.last_contacted IS NULL OR contact_logs.last_contacted < CURRENT_DATE - INTERVAL %s DAY;
    
#     """,day,as_dict=1)

@frappe.whitelist()
def get_last_contacted(from_date,to_date):

    data = frappe.db.sql("""
    SELECT c.name,c.custom_sales_person,c.custom_client_tiers
    FROM `tabCustomer` c
    LEFT JOIN (
        SELECT customer, MAX(contacted_date) AS last_contacted
        FROM (
            SELECT message_to as customer, sent_on as contacted_date FROM `tabAetas WhatsApp Log`
            UNION ALL
            SELECT call_to as customer, call_initiated_at as contacted_date FROM `tabAetas Call Log`
        ) AS combined_logs
        GROUP BY customer
    ) AS contact_logs ON c.name = contact_logs.customer
    WHERE (contact_logs.last_contacted IS NULL OR contact_logs.last_contacted < CURRENT_DATE)
    AND contact_logs.last_contacted BETWEEN %s AND %s;
    
    """,(from_date, to_date), as_dict=1)
    if not data:
        frappe.throw("No data found for the specified criteria")
    return data

    