import frappe
from crm_application_plugin.api.utils import create_response
from frappe.utils import getdate

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


def get_boutique_for_current_user():
    sales_person = get_sales_person_for_current_user()
    if not sales_person:
        return None

    boutique = frappe.db.get_value("Sales Person", sales_person, "custom_botique")
    return boutique


@frappe.whitelist()
def get_open_leads():
    form = frappe.local.form_dict

    offset = int(form.get("offset", 0))
    limit = int(form.get("limit", 20))
    search = (form.get("search") or "").strip()

    sales_person = get_sales_person_for_current_user()
    if not sales_person:
        return create_response(403, "No Sales Person found for current user")

    # Get the current user's store/boutique
    current_user_boutique = frappe.db.get_value(
        "Sales Person", sales_person, "custom_botique"
    )

    if not current_user_boutique:
        return create_response(403, "Current Sales Person has no Boutique assigned")

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

    query = f"""
        SELECT
            l.name,
            l.lead_name,
            l.customer,
            IFNULL(l.email_id, '') AS email_id,
            IFNULL(l.mobile_no, '') AS mobile_no,
            IFNULL(l.custom_brand, '') AS brand,
            IFNULL(l.custom_model, '') AS model,
            IFNULL(l.custom_itemservice, '') AS item_service,
            IFNULL(l.custom_preferred_store, '') AS preferred_store,
            l.status,
            IFNULL(l.custom_sales_person, '') AS sales_person,
            
            -- [FLAG] 1 if this user already applied, 0 otherwise
            IF(self_bid_check.name IS NOT NULL, 1, 0) AS is_applied

        FROM `tabLead` l
        
        -- Check if ANYONE has an 'Approved' bid (to exclude the lead entirely)
        LEFT JOIN `tabSales Person Bids` approved_check 
            ON approved_check.parent = l.name 
            AND approved_check.parenttype = 'Lead'
            AND TRIM(approved_check.status) = 'Approved'

        -- Check if CURRENT USER has a bid (to set is_applied flag)
        LEFT JOIN `tabSales Person Bids` self_bid_check
            ON self_bid_check.parent = l.name
            AND self_bid_check.parenttype = 'Lead'
            AND self_bid_check.sales_person = %s

        WHERE
            l.status IN ('Open' , 'Qualified')
            
            -- 1. STRICT: Lead must belong to the user's boutique
            AND l.custom_preferred_store = %s
            
            -- 2. EXCLUDE: If the lead is already won (Approved) by anyone
            AND approved_check.name IS NULL

            {search_cond}
        ORDER BY l.modified DESC
        LIMIT %s OFFSET %s
    """

    # Parameter Binding Order:
    # 1. sales_person (for self_bid_check)
    # 2. current_user_boutique (for preferred_store match)
    # 3. search params (if any)
    # 4. limit
    # 5. offset
    query_params = tuple(
        [sales_person, current_user_boutique] + params + [limit, offset]
    )

    leads = frappe.db.sql(query, query_params, as_dict=True)

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
        return create_response(403, "No Sales Person found for current user")

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
            l.customer,
            IFNULL(l.email_id, '') AS email_id,
            IFNULL(l.mobile_no, '') AS mobile_no,
            IFNULL(l.custom_brand, '') AS brand,
            IFNULL(l.custom_model, '') AS model,
            IFNULL(l.custom_itemservice, '') AS item_service,
            IFNULL(l.custom_preferred_store, '') AS preferred_store,
            l.status,
            spb.status as bid_status
        FROM `tabLead` l
        JOIN `tabSales Person Bids` spb ON l.name = spb.parent
        WHERE 
            spb.sales_person = %s
            
            -- [CHANGE] Filter for Approved status only (using TRIM for safety)
            AND TRIM(spb.status) = 'Approved'
            
            AND l.status != 'Cold'
            {search_cond}
        ORDER BY l.modified DESC
        LIMIT %s OFFSET %s
        """,
        tuple([sales_person] + params + [limit, offset]),
        as_dict=True,
    )

    if not leads:
        return create_response(
            200,
            message=f"No approved leads found for Sales Person {sales_person}",
            data=[],
        )

    return create_response(
        200, message="Approved leads fetched successfully", data=leads
    )


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


@frappe.whitelist()
def set_lead_warm(lead_name, followup_date):
    if not lead_name:
        create_response(406, "Lead name is required")
        return

    doc = frappe.get_doc("Lead", lead_name)
    if not doc:
        create_response(406, f"Lead not found: {lead_name}")
        return

    if doc.status == "Warm":
        create_response(409, f"Lead {lead_name} is already Warm")
        return

    doc.status = "Warm"
    doc.custom_followup_date = getdate(followup_date)
    doc.save()


@frappe.whitelist()
def get_my_warm_leads():
    sales_person = get_sales_person_for_current_user()
    if not sales_person:
        return create_response(403, "No Sales Person found for current user")

    # Fetch leads where status is Warm AND current user has an Approved bid
    query = """
        SELECT
            l.name,
            l.lead_name AS customer_name,
            l.custom_followup_date AS followup_date
        FROM
            `tabLead` l
        INNER JOIN
            `tabSales Person Bids` spb ON l.name = spb.parent
        WHERE
            l.status = 'Warm'
            AND spb.parenttype = 'Lead'
            AND spb.sales_person = %s
            AND spb.status = 'Approved'
            AND l.custom_preferred_store = %s
            AND l.custom_preferred_store IS NOT NULL
            AND l.custom_preferred_store != ''
            AND l.custom_followup_date IS NOT NULL
            AND l.custom_followup_date != ''
            AND l.custom_followup_date <= %s
        ORDER BY
            l.custom_followup_date ASC
    """
    current_user_boutique = get_boutique_for_current_user()
    leads = frappe.db.sql(
        query,
        (sales_person, current_user_boutique, frappe.utils.nowdate()),
        as_dict=True,
    )

    if not leads:
        return create_response(200, "No warm leads found", [])

    return create_response(200, "Warm leads fetched successfully", leads)


@frappe.whitelist()
def get_lead_journey_logs(lead_name: str) -> None:
    """
    Fetches all rows from the 'custom_lead_journey' table for a specific Lead.
    """
    try:
        if not lead_name:
            create_response(422, "Missing Data", "Please provide a lead_name.")
            return

        # 1. Check if Lead exists
        if not frappe.db.exists("Lead", lead_name):
            create_response(404, "Not Found", "Lead does not exist.")
            return

        # 2. Dynamically get the Child Doctype name from the Lead Meta
        # This prevents errors if you rename the Child Doctype later.
        lead_meta = frappe.get_meta("Lead")
        field_meta = lead_meta.get_field("custom_lead_journey")

        if not field_meta:
            create_response(
                500, "Config Error", "Field 'custom_lead_journey' not found in Lead."
            )
            return

        child_doctype_name = field_meta.options  # This holds the Child Doctype Name

        # 3. Fetch the Child Table rows efficiently
        logs = frappe.get_all(
            child_doctype_name,
            filters={
                "parent": lead_name,
                "parentfield": "custom_lead_journey",
                "parenttype": "Lead",
            },
            fields=[
                "name",
                "by_user",
                "to_customer",
                "mobile_number",
                "type",
                "initiated_at",
            ],
            order_by="initiated_at desc",
        )

        create_response(200, "Logs fetched successfully", logs)
        return

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Get Lead Journey Failed")
        create_response(406, "Failed", "An error occurred while fetching logs.")
        return
