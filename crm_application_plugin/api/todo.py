import frappe
from crm_application_plugin.api.utils import create_response

@frappe.whitelist()
def todo_list(date):
    user = frappe.session.user
    #get list of todo for perticular date for perticular user
    todo_list = frappe.db.sql("""
    select t.description
    from`tabToDo` t
    where t.allocated_to = %(user)s and date = %(date)s
    """,{'user':user,'date':date},as_dict=1)

    if todo_list:
        create_response(200,"ToDo List Fetched successfully",todo_list)
        return
    else:
        create_response(404,"No Records Found for ToDo list")
        return


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
