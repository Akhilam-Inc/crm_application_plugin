import frappe
from functools import reduce

def create_response(status,message,data=None):
    frappe.local.response.http_status_code = status
    frappe.local.response.message = message
    if data is not None:
        frappe.local.response.data = data
        
        
def group_data(items):
    
    return reduce(group_by_key , items , {})

def group_by_key(acc, data):
    key = data["formatted_date"]
    if key not in acc:
        acc[key] = []
        
    acc[key].append(data)
    
    return acc    
        