import frappe
from crm_application_plugin.api.utils import create_response,group_data
from datetime import timedelta

# @frappe.whitelist()
# def todo_list(date):
#     search = frappe.local.form_dict.search or ""
#     offset = int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0

#     condition = ""
#     condition_params = {}
#     if search:
#         condition += "AND t.description LIKE %(search)s"
#         condition_params['search'] = f"%{search}%"

#     user = frappe.session.user
#     todo_list = frappe.db.sql(f"""
#         SELECT t.description
#         FROM `tabToDo` t
#         WHERE t.allocated_to = %(user)s AND date = %(date)s {condition}
#         LIMIT %(offset)s, 20
#     """, {'user': user, 'date': date, 'offset': offset, **condition_params}, as_dict=1)

#     if todo_list:
#         create_response(200, "ToDo List Fetched successfully", todo_list)
#         return
#     else:
#         create_response(404, "No Records Found for ToDo list")
#         return



@frappe.whitelist()
def create_todo(task_name, date):
    try:
        user_id = frappe.session.user
        todo = frappe.new_doc("ToDo")
        todo.description = task_name
        todo.status = 'Open'
        todo.priority = 'Medium'
        todo.allocated_to = user_id
        todo.date = date
        todo_record = todo.insert(ignore_permissions= 1)
        create_response(200,"ToDo created successfully",todo_record.name)
        return
    except Exception as e:
        create_response(406,"ToDo creation failed",frappe.get_traceback())
        return

@frappe.whitelist()
def todo_list(date):
    try:
        search = frappe.local.form_dict.search or ""    
        date = frappe.utils.getdate(date)
        
        start_date = date - timedelta(days=15)
        end_date = date + timedelta(days=15)
        
        condition = ""
        condition_params = {}
        if search:
            condition += "AND t.description LIKE %(search)s"
            condition_params['search'] = f"%{search}%"
        
        # return condition_params
        
        sql_data =  frappe.db.sql(f"""
        SELECT date as formatted_date, description
        FROM `tabToDo`
        WHERE date BETWEEN %(start_date_str)s AND %(end_date_str)s AND allocated_to = %(user)s {condition}      
        """,{'start_date_str':start_date,'end_date_str':end_date,'user':frappe.session.user, **condition_params},as_dict=1)
        
        # return sql_data
        
        group_todos = group_data(sql_data)
        
        create_response(200, "ToDo List Fetched successfully", sql_data)
            
    except Exception as e:
        return create_response(406, "List fetch error", frappe.get_traceback())

    
    
        
    
    
