import frappe
from crm_application_plugin.api.utils import create_response
from frappe.utils import now_datetime


@frappe.whitelist()
def create_call_log(call_by, call_to, mobile_no):
    try:
        if not call_by or not call_to or not mobile_no:
            create_response(
                422,
                "Invalid request data",
                "Please provide call_by, call_to, and mobile_no.",
            )
            return

        call_obj = frappe.new_doc("Aetas Call Log")
        call_obj.call_by = call_by
        call_obj.call_to = call_to
        call_obj.call_initiated_at = frappe.utils.now()
        call_obj.mobile_number = mobile_no
        call_doc = call_obj.insert(ignore_permissions=1)

        create_response(200, "Aetas Call Log created successfully", call_doc.name)
        return

    except Exception:
        create_response(406, "Aetas Call Log creation failed", frappe.get_traceback())
        return


@frappe.whitelist()
def create_whatsapp_log(message_by, message_to, mobile_no, message, default=0):
    try:
        if not message_by or not message_to or not mobile_no:
            create_response(
                422,
                "Invalid request data",
                "Please provide message_by, message_to, and mobile_no.",
            )
            return

        whatsapp_obj = frappe.new_doc("Aetas WhatsApp Log")
        whatsapp_obj.message_by = message_by
        whatsapp_obj.message_to = message_to
        whatsapp_obj.sent_on = frappe.utils.now()
        whatsapp_obj.mobile_number = mobile_no
        whatsapp_obj.message = message
        whatsapp_obj.default_message = default
        whatsapp_doc = whatsapp_obj.insert(ignore_permissions=1)

        create_response(200, "Aetas Call Log created successfully", whatsapp_doc.name)
        return

    except Exception:
        create_response(406, "Aetas Call Log creation failed", frappe.get_traceback())
        return


@frappe.whitelist()
def create_lead_log(
    lead_name: str, by_user: str, to_customer: str, mobile_no: str, log_type: str
) -> None:
    """
    Creates a new log entry inside the Lead's child table based on the provided screenshot fields.
    """
    try:
        if not all([lead_name, by_user, mobile_no]):
            create_response(
                422,
                "Invalid request data",
                "Please provide lead_name, by_user and mobile_no.",
            )
            return

        if not frappe.db.exists("Lead", lead_name):
            create_response(404, "Not Found", f"Lead {lead_name} does not exist.")
            return

        # lead_doc = frappe.get_doc("Lead", lead_name)

        # new_row = lead_doc.append(
        #     "custom_lead_journey",
        #     {
        #         "parent": lead_name,
        #         "by_user": by_user,
        #         "to_customer": to_customer,
        #         "mobile_number": mobile_no,
        #         "log_type": log_type,
        #         "initiated_at": initiated_at or now(),
        #     },
        # )

        # lead_doc.save(ignore_permissions=True)
        child_doc_data = {
            "doctype": "Lead Journey",  # <--- REPLACE THIS (e.g., "Lead Call Log")
            "parent": lead_name,  # The Lead ID
            "parenttype": "Lead",  # The Parent Doctype
            "parentfield": "custom_lead_journey",  # The Field Name in Lead (Confirmed)
            # Your Data Fields
            "by_user": by_user,
            "to_customer": to_customer,
            "mobile_number": mobile_no,
            "type": log_type,
            "initiated_at": now_datetime(),
        }

        # 3. Create and Insert the Document
        child_doc = frappe.get_doc(child_doc_data)
        child_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        create_response(200, "Lead log added successfully", child_doc.name)
        return

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Lead Child Log Creation Failed")
        create_response(
            406, "Log creation failed", "An error occurred while updating the Lead."
        )
        return
