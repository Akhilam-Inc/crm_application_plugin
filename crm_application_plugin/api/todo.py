import frappe
from crm_application_plugin.api.utils import create_response,group_data
from datetime import timedelta
import itertools

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
        SELECT date , description, reference_type, reference_name, status, custom_customer
        FROM `tabToDo`
        WHERE date BETWEEN %(start_date_str)s AND %(end_date_str)s AND allocated_to = %(user)s {condition}      
        """,{'start_date_str':start_date,'end_date_str':end_date,'user':frappe.session.user, **condition_params},as_dict=1)
        
        grouped_todos = {}
        for row in sql_data:
            date = row['date'].strftime('%Y-%m-%d')
            if date not in grouped_todos:
                grouped_todos[date] = []
            grouped_todos[date].append(row)
        
        
        create_response(200, "ToDo List Fetched successfully", grouped_todos)
    except Exception as e:
        return create_response(406, "List fetch error", frappe.get_traceback())

    
    
        
    
    
