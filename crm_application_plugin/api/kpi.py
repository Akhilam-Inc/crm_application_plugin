import frappe
from crm_application_plugin.api.utils import create_response
from frappe.utils import get_first_day, get_last_day, today

@frappe.whitelist()
def target():
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406,"Employee not found")
        return
    
    sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
    if not sales_person:
        create_response(406,"Sales Person not found")
        return
    
    sales_persons = frappe.local.form_dict.sales_persons or ""
    get_current_month = frappe.utils.data.getdate(frappe.utils.data.nowdate()).strftime("%B")
    
    active_fiscal_year = frappe.db.get_value("Fiscal Year",{"year_start_date":["<=",frappe.utils.data.nowdate()],"year_end_date":[">=",frappe.utils.data.nowdate()],"disabled":0},"name")
    
    target_for_current_month = get_target([sales_person] + sales_persons.split(","),get_current_month,active_fiscal_year)
    
    target = target_for_current_month[0].tg_amt if target_for_current_month else 0
        
    create_response(200,"Success",{"target":target})
    return

# @frappe.whitelist()    
# def achvievement():
#     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#     if not employee:
#         create_response(406,"Employee not found")
#         return
    
#     sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
#     if not sales_person:
#         create_response(406,"Sales Person not found")
#         return
    
#     sales_persons = frappe.local.form_dict.sales_persons or ""
    
#     sales_target_achieved_for_current_month = get_achived([sales_person] + sales_persons.split(","))
    
#     achieved = sales_target_achieved_for_current_month[0]['sales'] if sales_target_achieved_for_current_month else 0
    
#     response_data = {
#         "achvievement": achieved,
#         "unit_per_transaction":sales_target_achieved_for_current_month[0]['unit_per_trans'] if sales_target_achieved_for_current_month else 0,
#         "avg_amt_per_invoice":sales_target_achieved_for_current_month[0]['avg_amt_per_invoice'] if sales_target_achieved_for_current_month else 0
#     }
#     create_response(200,"Success",response_data)
#     return
@frappe.whitelist()    
def achvievement():
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406,"Employee not found")
        return
    
    sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
    if not sales_person:
        create_response(406,"Sales Person not found")
        return
    
    sales_persons = frappe.local.form_dict.sales_persons or ""

    # build list once so we can reuse it
    extra_sales_persons = sales_persons.split(",") if sales_persons else []
    sales_person_list = [sales_person] + extra_sales_persons

    sales_target_achieved_for_current_month = get_achived(sales_person_list)

    achieved = (
        sales_target_achieved_for_current_month[0]["sales"]
        if sales_target_achieved_for_current_month else 0
    )

    # keep originals as they are now
    unit_per_transaction = (
        sales_target_achieved_for_current_month[0]["unit_per_trans"]
        if sales_target_achieved_for_current_month else 0
    )
    avg_amt_per_invoice = (
        sales_target_achieved_for_current_month[0]["avg_amt_per_invoice"]
        if sales_target_achieved_for_current_month else 0
    )

    # 🔹 NEW: get Watch qty
    watch_qty = get_watch_qty_for_sales_persons(sales_person_list)

    # divide totals by Watch qty (with zero safety)
    if watch_qty:
        unit_per_transaction = unit_per_transaction / watch_qty
        avg_amt_per_invoice = avg_amt_per_invoice / watch_qty
    else:
        unit_per_transaction = 0
        avg_amt_per_invoice = 0

    response_data = {
        "achvievement": achieved,
        "unit_per_transaction": unit_per_transaction,
        "avg_amt_per_invoice": avg_amt_per_invoice,
    }
    create_response(200, "Success", response_data)
    return


def get_target(sales_person_list, month, fiscal_year):
    target_for_current_month = frappe.db.sql("""
    select td.name, td.target_amount, td.distribution_id, mdp.month, mdp.percentage_allocation, (sum(td.target_amount) * mdp.percentage_allocation) / 100 as tg_amt 
    from `tabTarget Detail` td 
    inner join `tabMonthly Distribution Percentage` mdp on td.distribution_id = mdp.parent  
    where td.parent IN %(sales_person_list)s and td.fiscal_year = %(fiscal_year)s and mdp.month = %(month)s group by mdp.month                                        
    """, {"sales_person_list": sales_person_list, "fiscal_year": fiscal_year, "month": month}, as_dict=1)
    
   
    return target_for_current_month

def get_achived(sales_person_list):
    sales_target_achieved_for_current_month = frappe.db.sql("""
    select sum(sii.amount) as sales,count(si.name) as si_count,sum(sii.qty) as itm_qty,sum(sii.qty)/count(si.name) as unit_per_trans,sum(sii.amount)/count(si.name) as avg_amt_per_invoice  from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on sii.parent = si.name where si.docstatus = 1 and sii.sales_person IN %(sales_person_list)s and month(si.posting_date) = month(now()) and year(si.posting_date) = year(now()) group by month(si.posting_date),year(si.posting_date)""",{ "sales_person_list": sales_person_list},as_dict=1)
    
    return sales_target_achieved_for_current_month

    

@frappe.whitelist()
def botique_target():
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406,"Employee not found")
        return 
    
    sales_person_botique = frappe.db.get_value("Sales Person", {"employee": employee}, "custom_botique")
    if not sales_person_botique:
        create_response(406,"Botique not found")
        return
    
    botiques = frappe.local.form_dict.botiques or ""
    
    botiue_sales_person_list = frappe.db.get_all("Sales Person", {"custom_botique": ["IN" , [sales_person_botique] + botiques.split(",")]}, "name",pluck="name")

    get_current_month = frappe.utils.data.getdate(frappe.utils.data.nowdate()).strftime("%B")
    
    active_fiscal_year = frappe.db.get_value("Fiscal Year",{"year_start_date":["<=",frappe.utils.data.nowdate()],"year_end_date":[">=",frappe.utils.data.nowdate()],"disabled":0},"name")    
    
    target_for_current_month = get_target(botiue_sales_person_list,get_current_month,active_fiscal_year)
    
    target = target_for_current_month[0].tg_amt if target_for_current_month else 0
        
    create_response(200,"Success",{"target":target})
    return
    
# @frappe.whitelist()
# def botique_achvievement():
#     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#     if not employee:
#         create_response(406,"Employee not found")
#         return 
    
#     sales_person_botique = frappe.db.get_value("Sales Person", {"employee": employee}, "custom_botique")
#     if not sales_person_botique:
#         create_response(406,"Botique not found")
#         return
    
#     botiques = frappe.local.form_dict.botiques or ""
    
#     botiue_sales_person_list = frappe.db.get_all("Sales Person", {"custom_botique": ["IN" , [sales_person_botique] + botiques.split(",")]}, "name",pluck="name")
    
#     sales_target_achieved_for_current_month = get_achived(botiue_sales_person_list)
#     # achieved = sales_target_achieved_for_current_month[0]['sales'] if sales_target_achieved_for_current_month else 0

#     sales_target_achieved_for_current_month_by_cost_center = boutique_achievement_by_cost_center([sales_person_botique] + botiques.split(","))
#     achieved = sales_target_achieved_for_current_month_by_cost_center if sales_target_achieved_for_current_month_by_cost_center else 0
    
#     response_data = {
#         "achvievement": achieved,
#         "unit_per_transaction":sales_target_achieved_for_current_month[0]['unit_per_trans'] if sales_target_achieved_for_current_month else 0,
#         "avg_amt_per_invoice":sales_target_achieved_for_current_month[0]['avg_amt_per_invoice'] if sales_target_achieved_for_current_month else 0
#     }
#     create_response(200,"Success",response_data)
#     return
@frappe.whitelist()
def botique_achvievement():
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406,"Employee not found")
        return 
    
    sales_person_botique = frappe.db.get_value("Sales Person", {"employee": employee}, "custom_botique")
    if not sales_person_botique:
        create_response(406,"Botique not found")
        return
    
    botiques = frappe.local.form_dict.botiques or ""
    
    botiue_sales_person_list = frappe.db.get_all(
        "Sales Person",
        {"custom_botique": ["IN", [sales_person_botique] + botiques.split(",")]},
        "name",
        pluck="name",
    )
    
    sales_target_achieved_for_current_month = get_achived(botiue_sales_person_list)

    sales_target_achieved_for_current_month_by_cost_center = boutique_achievement_by_cost_center(
        sales_person_botique
    )
    achieved = (
        sales_target_achieved_for_current_month_by_cost_center
        if sales_target_achieved_for_current_month_by_cost_center
        else 0
    )

    # keep existing totals
    unit_per_transaction = (
        sales_target_achieved_for_current_month[0]["unit_per_trans"]
        if sales_target_achieved_for_current_month else 0
    )
    avg_amt_per_invoice = (
        sales_target_achieved_for_current_month[0]["avg_amt_per_invoice"]
        if sales_target_achieved_for_current_month else 0
    )

    # 🔹 NEW: Watch qty for all sales persons under the selected boutiques
    watch_qty = get_watch_qty_for_sales_persons(botiue_sales_person_list)

    if watch_qty:
        unit_per_transaction = unit_per_transaction / watch_qty
        avg_amt_per_invoice = avg_amt_per_invoice / watch_qty
    else:
        unit_per_transaction = 0
        avg_amt_per_invoice = 0
    
    response_data = {
        "achvievement": achieved,
        "unit_per_transaction": unit_per_transaction,
        "avg_amt_per_invoice": avg_amt_per_invoice,
    }
    create_response(200, "Success", response_data)
    return


def boutique_achievement_by_cost_center(boutiques):
    """
    boutiques: list of Boutique names (or a comma-separated string).
    Sums achievement for ALL boutiques' cost centers.
    """
    if isinstance(boutiques, str):
        boutiques = [b.strip() for b in boutiques.split(",") if b.strip()]

    if not boutiques:
        return 0

    # get all cost centers mapped to these boutiques
    cost_centers = frappe.get_all(
        "Boutique",
        filters={"name": ["in", boutiques]},
        pluck="boutique_cost_center",
    )

    cost_centers = [c for c in cost_centers if c]
    if not cost_centers:
        return 0

    first_day_of_month = get_first_day(today())
    last_day_of_month = get_last_day(today())

    result = frappe.db.sql(
        """
        SELECT COALESCE(SUM(sii.amount), 0) AS total_amount
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE
            si.docstatus = 1
            AND sii.cost_center IN %(cost_centers)s
            AND si.posting_date BETWEEN %(start_date)s AND %(end_date)s
        """,
        {
            "cost_centers": tuple(cost_centers),
            "start_date": first_day_of_month,
            "end_date": last_day_of_month,
        },
        as_dict=1,
    )

    return result[0].total_amount if result else 0

def get_watch_qty_for_sales_persons(sales_person_list):
    """Total qty of sold items in Watch category for given sales persons (current month)."""
    watch_qty_data = frappe.db.sql("""
        SELECT
            COALESCE(SUM(sii.qty), 0) AS watch_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE
            si.docstatus = 1
            AND sii.sales_person IN %(sales_person_list)s
            AND i.item_group = 'Watch'
            AND MONTH(si.posting_date) = MONTH(CURDATE())
            AND YEAR(si.posting_date) = YEAR(CURDATE())
    """, {
        "sales_person_list": sales_person_list
    }, as_dict=1)

    return watch_qty_data[0]["watch_qty"] if watch_qty_data else 0
