
import frappe
import json

@frappe.whitelist()
def mark_incognito(names):
    if isinstance(names, str):
        names = json.loads(names)
    for name in names:
        _mark_incognito(name)
    frappe.msgprint("Customers Marked as Incognito")

def _mark_incognito(name):
    try:
        frappe.db.set_value("Customer" , name , {
            "custom_incognito" : 1
        })
    except Exception as e:
        frappe.log_error(title="Bulk Mark Customer Incognito" , message= f"{frappe.get_traceback(e)}") 