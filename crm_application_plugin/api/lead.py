import frappe
from crm_application_plugin.api.utils import create_response

# from crm_application_plugin.api.customer import sales_person_list


def get_sales_person_for_current_user():
    user = frappe.session.user

    emp = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not emp:
        create_response(406, f"User not linked with Employee: {user}")
        return

    sales_person = frappe.db.get_value("Sales Person", {"employee": emp}, "name")
    if not sales_person:
        create_response(406, f"Employee not linked with Sales Person: {emp}")
        return

    return sales_person


@frappe.whitelist()
def get_open_leads():
    form = frappe.local.form_dict

    offset = int(form.get("offset", 0))
    limit = int(form.get("limit", 20))
    search = (form.get("search") or "").strip()

    sales_person = get_sales_person_for_current_user()
    if not sales_person:
        return

    search_cond = ""
    params = []

    if search:
        search_cond = """
            AND (
                l.lead_name LIKE %s
                OR l.name LIKE %s
            )
        """
        val = f"%{search}%"
        params.extend([val, val])

    leads = frappe.db.sql(
        f"""
        SELECT
            l.name,
            l.lead_name,
            IFNULL(l.email_id, '') AS email_id,
            IFNULL(l.mobile_no, '') AS mobile_no,
            IFNULL(l.custom_brand, '') AS brand,
            IFNULL(l.custom_model, '') AS model,
            IFNULL(l.custom_itemservice, '') AS item_service,
            IFNULL(l.custom_preferred_store, '') AS preferred_store,
            l.status,
            IFNULL(l.custom_sales_person, '') AS sales_person
        FROM `tabLead` l
        WHERE
            l.status = 'Open'
            AND NOT EXISTS (
                SELECT 1
                FROM `tabSales Person Bids` spb
                WHERE
                    spb.parent = l.name
                    AND spb.parenttype = 'Lead'
                    AND spb.sales_person = %s
            )
            {search_cond}
        ORDER BY l.modified DESC
        LIMIT %s OFFSET %s
        """,
        tuple([sales_person] + params + [limit, offset]),
        as_dict=True,
    )

    if not leads:
        return create_response(200, message="No open leads found", data=[])

    return create_response(
        200,
        message="Open leads fetched successfully",
        data=leads,
    )


@frappe.whitelist()
def add_sales_person_to_lead(lead_name):
    try:
        if not lead_name:
            create_response(406, "Lead name is required")
            return

        sales_person = get_sales_person_for_current_user()

        doc = frappe.get_doc("Lead", lead_name)
        if not doc:
            create_response(406, f"Lead not found: {lead_name}")
            return

        today = frappe.utils.nowdate()

        already_exists = any(
            row.sales_person == sales_person for row in doc.custom_bids
        )

        if already_exists:
            create_response(
                409, f"Sales Person {sales_person} already assigned to Lead {lead_name}"
            )
            return

        doc.append(
            "custom_bids",
            {
                "sales_person": sales_person,
                "status": "Applied",
                "applied_on": today,
            },
        )

        doc.save(ignore_permissions=True)

        return create_response(
            200, f"Sales Person {sales_person} added to Lead {lead_name}"
        )

    except frappe.ValidationError as e:
        return create_response(406, str(e))


@frappe.whitelist()
def get_leads_of_applied_sales_person():
    form = frappe.local.form_dict
    offset = int(form.get("offset", 0))
    limit = int(form.get("limit", 20))
    search = (form.get("search") or "").strip()

    sales_person = get_sales_person_for_current_user()
    if not sales_person:
        return

    search_cond = ""
    params = []

    if search:
        search_cond = """
            AND (
                l.lead_name LIKE %s
                OR l.name LIKE %s
            )
        """
        val = f"%{search}%"
        params.extend([val, val])

    leads = frappe.db.sql(
        f"""
        SELECT DISTINCT
            l.name,
            l.lead_name,
            IFNULL(l.email_id, '') AS email_id,
            IFNULL(l.mobile_no, '') AS mobile_no,
            IFNULL(l.custom_brand, '') AS brand,
            IFNULL(l.custom_model, '') AS model,
            IFNULL(l.custom_itemservice, '') AS item_service,
            IFNULL(l.custom_preferred_store, '') AS preferred_store,
            l.status
        FROM `tabLead` l
        JOIN `tabSales Person Bids` spb ON l.name = spb.parent
        WHERE spb.sales_person = %s
        AND l.status != 'Cold'
        {search_cond}
        ORDER BY l.modified DESC
        LIMIT %s OFFSET %s
        """,
        tuple([sales_person] + params + [limit, offset]),
        as_dict=True,
    )

    if not leads:
        return create_response(200, message="No leads found for Sales Person {sales_person}", data=[])

    return create_response(200, message="Leads fetched successfully", data=leads)


@frappe.whitelist()
def set_lead_status(lead_name, cold_description=None):
    if not lead_name:
        create_response(406, "Lead name is required")
        return

    doc = frappe.get_doc("Lead", lead_name)
    if not doc:
        create_response(406, f"Lead not found: {lead_name}")
        return

    if doc.status == "Cold":
        create_response(409, f"Lead {lead_name} is already Cold")
        return

    doc.status = "Cold"
    doc.custom_cold_description = cold_description
    doc.save()
