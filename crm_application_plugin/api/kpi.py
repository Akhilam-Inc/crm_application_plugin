import frappe
from crm_application_plugin.api.utils import create_response

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
        
    get_current_month = frappe.utils.data.getdate(frappe.utils.data.nowdate()).strftime("%B")
    
    active_fiscal_year = frappe.db.get_value("Fiscal Year",{"year_start_date":["<=",frappe.utils.data.nowdate()],"year_end_date":[">=",frappe.utils.data.nowdate()],"disabled":0},"name")
    
    target_for_current_month = get_target([sales_person],get_current_month,active_fiscal_year)
    
    target = target_for_current_month[0].tg_amt if target_for_current_month else 0
        
    create_response(200,"Success",{"target":target})
    return

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
        
    sales_target_achieved_for_current_month = get_achived([sales_person])
    
    achieved = sales_target_achieved_for_current_month[0]['sales'] if sales_target_achieved_for_current_month else 0
    
    response_data = {
        "achvievement": achieved,
        "unit_per_transaction":sales_target_achieved_for_current_month[0]['unit_per_trans'] if sales_target_achieved_for_current_month else 0,
        "avg_amt_per_invoice":sales_target_achieved_for_current_month[0]['avg_amt_per_invoice'] if sales_target_achieved_for_current_month else 0
    }
    create_response(200,"Success",response_data)
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
    select sum(sii.amount) as sales,count(si.name) as si_count,sum(sii.qty) as itm_qty,sum(sii.qty)/count(si.name) as unit_per_trans,sum(sii.amount)/count(si.name) as avg_amt_per_invoice  from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on sii.parent = si.name where si.docstatus = 1 and sii.custom_sales_person IN %(sales_person_list)s and month(si.posting_date) = month(now()) and year(si.posting_date) = year(now()) group by month(si.posting_date),year(si.posting_date)""",{ "sales_person_list": sales_person_list},as_dict=1)
    
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
    
    botiue_sales_person_list = frappe.db.get_all("Sales Person", {"custom_botique": sales_person_botique}, "name",pluck="name")

    
    get_current_month = frappe.utils.data.getdate(frappe.utils.data.nowdate()).strftime("%B")
    
    active_fiscal_year = frappe.db.get_value("Fiscal Year",{"year_start_date":["<=",frappe.utils.data.nowdate()],"year_end_date":[">=",frappe.utils.data.nowdate()],"disabled":0},"name")    
    
    target_for_current_month = get_target(botiue_sales_person_list,get_current_month,active_fiscal_year)
    
    target = target_for_current_month[0].tg_amt if target_for_current_month else 0
        
    create_response(200,"Success",{"target":target})
    return
    
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
    
    botiue_sales_person_list = frappe.db.get_all("Sales Person", {"custom_botique": sales_person_botique}, "name",pluck="name")
    
    sales_target_achieved_for_current_month = get_achived(botiue_sales_person_list)
    
    achieved = sales_target_achieved_for_current_month[0]['sales'] if sales_target_achieved_for_current_month else 0
    
    response_data = {
        "achvievement": achieved,
        "unit_per_transaction":sales_target_achieved_for_current_month[0]['unit_per_trans'] if sales_target_achieved_for_current_month else 0,
        "avg_amt_per_invoice":sales_target_achieved_for_current_month[0]['avg_amt_per_invoice'] if sales_target_achieved_for_current_month else 0
    }
    create_response(200,"Success",response_data)
    return
    
    

    
    
