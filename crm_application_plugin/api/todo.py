import frappe
from crm_application_plugin.api.utils import create_response

@frappe.whitelist()
def todo_list():
    user = frappe.session.user

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
    except Exception as e:
        create_response(406,"ToDo creation failed",frappe.get_traceback())
