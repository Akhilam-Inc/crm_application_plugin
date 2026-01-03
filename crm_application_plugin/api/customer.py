import frappe
from crm_application_plugin.api.home import get_sales_person_herarchy
from crm_application_plugin.api.utils import create_response
from frappe.contacts.doctype.address.address import get_address_display


@frappe.whitelist()
def get_assigned_customer_list(salesperson=None):
    # user = frappe.session.user
    # Implement Serach Function
    # Get Frappe user from session, Get Employee for that user and fetch sales person for that employee.
    # Get All Customers where the sales person is mentioned in sales team
    try:
        search = frappe.local.form_dict.search or ""
        tier = frappe.local.form_dict.tier or ""
        campaign = frappe.local.form_dict.campaign or ""
        offset = (
            int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0
        )

        condition = ""
        if search is not None and search != "":
            condition += "and ((c.customer_name like %(search)s) or (c.contact_no like %(search)s) or (c.custom_contact like %(search)s)) "

        if tier is not None and tier != "":
            condition += "and c.custom_client_tiers = %(custom_client_tiers)s"

        user = frappe.session.user
        employee = frappe.get_value("Employee", {"user_id": user}, "name")
        if not employee:
            create_response(406, "Employee not found for the current user.")
            return

        sales_person = frappe.get_value("Sales Person", {"employee": employee}, "name")
        if not sales_person:
            create_response(406, "Sales Person not found for the current user.")
            return

        public_tiers = frappe.db.get_all(
            "Client Tiers", filters={"is_public": 1}, pluck="name"
        )

        if tier not in public_tiers:
            customer_data = frappe.db.sql(
                """
				SELECT c.name, c.customer_name, c.custom_sales_person, COALESCE(c.custom_contact, c.contact_no) AS mobile_no, c.email_id,c.custom_client_tiers,c.custom_incognito,
				(SELECT MAX(si.posting_date) FROM `tabSales Invoice` si WHERE si.customer = c.customer_name) AS last_purchase_date
				FROM `tabCustomer` c
				WHERE c.custom_sales_person in %(sales_person)s {conditions}  LIMIT %(offset)s,20
			""".format(conditions=condition),
                {
                    "sales_person": get_sales_person_herarchy(user, salesperson),
                    "search": "%" + search + "%",
                    "offset": int(offset),
                    "custom_client_tiers": tier,
                },
                as_dict=True,
            )
        else:
            customer_data = frappe.db.sql(
                """
				SELECT c.name, c.customer_name, c.custom_sales_person, COALESCE(c.custom_contact, c.contact_no) AS mobile_no, c.email_id,c.custom_client_tiers,c.custom_incognito,
				(SELECT MAX(si.posting_date) FROM `tabSales Invoice` si WHERE si.customer = c.customer_name) AS last_purchase_date
				FROM `tabCustomer` c
				WHERE c.custom_sales_person is null {conditions}  LIMIT %(offset)s,20
			""".format(conditions=condition),
                {
                    "sales_person": get_sales_person_herarchy(user, salesperson),
                    "search": "%" + search + "%",
                    "offset": int(offset),
                    "custom_client_tiers": tier,
                },
                as_dict=True,
            )

        for row in customer_data:
            campaigns = frappe.db.sql(
                """
			select custom_customer,reference_name as campaign_name,status from `tabToDo` inner join `tabCampaign` on `tabToDo`.reference_name = `tabCampaign`.name where `tabToDo`.custom_customer = %(customer)s and `tabCampaign`.custom_enable = 1         
			""",
                {"customer": row["name"]},
                as_dict=1,
            )
            row["campaigns"] = campaigns
            row["last_contacted_date"] = get_last_contacted_date(row["name"])

        if campaign:
            customer_data = list(
                filter(
                    lambda x: any(
                        camp["campaign_name"] == campaign for camp in x["campaigns"]
                    ),
                    customer_data,
                )
            )

        create_response(200, "Assigned Customer List Fetched!", customer_data)
        return

    except Exception as e:
        create_response(
            406, "An error occurred while getting assigned customer list", str(e)
        )
        return


@frappe.whitelist()
def get_last_contacted_date(customer):
    last_contacted_date = frappe.db.sql(
        """
		SELECT MAX(cl.contacted_date) AS last_contacted
		FROM (
			SELECT message_to as customer, sent_on as contacted_date FROM `tabAetas WhatsApp Log` where message_to = %(customer)s
			UNION ALL
			SELECT call_to as customer, call_initiated_at as contacted_date FROM `tabAetas Call Log` where call_to = %(customer)s
		) as cl""",
        {"customer": customer},
        as_dict=1,
    )
    return last_contacted_date[0]["last_contacted"] if last_contacted_date else None


@frappe.whitelist()
def get_unassigned_customer_list():
    try:
        search = frappe.local.form_dict.search or ""
        offset = (
            int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0
        )
        limit = 20

        condition = ""
        condition_params = {}
        if search is not None and search != "":
            condition += " AND ((c.customer_name LIKE %(search)s) or (c.contact_no LIKE %(search)s) or (c.custom_contact LIKE %(search)s))"
            condition_params["search"] = f"%{search}%"

        user = frappe.session.user
        employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
        if not employee:
            create_response(406, "Employee not found for the current user.")
            return

        sales_person = frappe.get_value("Sales Person", {"employee": employee}, "name")
        if not sales_person:
            create_response(406, "Sales Person not found for the current user.")
            return

        sql_query = f"""
			SELECT c.name, c.customer_name, COALESCE(c.custom_contact, c.contact_no) AS mobile_no, c.custom_sales_person, c.custom_incognito
			FROM `tabCustomer` c
			WHERE (c.custom_sales_person != %(sales_person)s OR c.custom_sales_person IS NULL) {condition}
			LIMIT %(offset)s, %(limit)s
		"""

        customer_list = frappe.db.sql(
            sql_query,
            {
                "sales_person": sales_person,
                "offset": offset,
                "limit": limit,
                **condition_params,
            },
            as_dict=1,
        )

        for customer in customer_list:
            customer["last_contacted_date"] = get_last_contacted_date(customer["name"])

        create_response(200, "Unassigned Customer List Fetched!", customer_list)
        return
    except Exception as e:
        create_response(
            409, "An error occurred while getting assigned customer list", str(e)
        )


# def get_last_contacted_date(customer):
#     last_contacted_date = frappe.db.sql(
#         """
# 		SELECT MAX(cl.contacted_date) AS last_contacted
# 		FROM (
# 			SELECT message_to as customer, sent_on as contacted_date FROM `tabAetas WhatsApp Log` where message_to = %(customer)s
# 			UNION ALL
# 			SELECT call_to as customer, call_initiated_at as contacted_date FROM `tabAetas Call Log` where call_to = %(customer)s
# 		) as cl""",
#         {"customer": customer},
#         as_dict=1,
#     )
#     return last_contacted_date[0]["last_contacted"] if last_contacted_date else None


@frappe.whitelist()
def get_past_purchase_customer():
    try:
        customer = frappe.local.form_dict.customer
        # Get Sales of this customer by based on customer parameter

        customer_sales_data = frappe.db.sql(
            """
		select si.posting_date,sii.item_name,sii.rate as price, i.image as image
		from`tabSales Invoice` si
		Inner Join`tabSales Invoice Item` sii on si.name = sii.parent
		LEFT JOIN `tabItem` i ON sii.item_code = i.item_code
		where si.customer = %(customer_name)s and si.docstatus = 1 and si.is_return = 0 and si.status != 'Credit Note Issued'
		order by si.posting_date desc
		""",
            {"customer_name": customer},
            as_dict=1,
        )

        create_response(
            200, "Past Purchase Of Customer List Fetched!", customer_sales_data
        )
        return
    except Exception as e:
        create_response(406, "An error occurred while fetching customer sales data", e)


@frappe.whitelist()
def create_customer(
    customer_name,
    mobile_number,
    email_address,
    address_line1,
    address_line2,
    city,
    state,
    pincode,
    country,
    boutique,
    sales_person,
    salutation,
    source,
    date_of_birth=None,
    anniversary_date=None,
):
    if not customer_name or not mobile_number:
        create_response(
            422, "Invalid request data", "Please provide all mandatory field data."
        )
        return

    if frappe.db.exists(
        "Customer", {"customer_name": customer_name, "custom_contact": mobile_number}
    ):
        create_response(
            409, "This customer name and contact combination already exists."
        )
        return

    try:
        customer_obj = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": customer_name,
                "salutation": salutation or "",
                "custom_contact": mobile_number,
                "customer_type": "Individual",
                "territory": "All Territories",
                "customer_group": "Individual",
                "custom_date_of_birth": date_of_birth or "",
                "custom_anniversary_date": anniversary_date or "",
                "boutique": boutique or "",
                "custom_sales_person": sales_person or "",
                "custom_source": source or "",
                "custom_custom_name": customer_name + " - " + mobile_number,
            }
        )

        customer_doc = customer_obj.insert(ignore_permissions=True)

        if mobile_number:
            contact_doc = frappe.get_doc(
                {
                    "doctype": "Contact",
                    "first_name": customer_name,
                    "phone_nos": [{"phone": mobile_number, "is_primary_mobile_no": 1}],
                    "links": [
                        {"link_doctype": "Customer", "link_name": customer_doc.name}
                    ],
                }
            )
        if email_address:
            contact_doc.append(
                "email_ids", {"email_id": email_address, "is_primary": 1}
            )
        contact_document = contact_doc.insert(ignore_permissions=True)

        if address_line1 and city and state and pincode and country:
            address_doc = frappe.get_doc(
                {
                    "doctype": "Address",
                    "address_type": "Billing",
                    "address_line1": address_line1,
                    "address_line2": address_line2,
                    "city": city,
                    "state": state,
                    "pincode": pincode,
                    "country": country,
                    "links": [
                        {"link_doctype": "Customer", "link_name": customer_doc.name}
                    ],
                }
            )

            add_doc = address_doc.insert(ignore_permissions=True)
            customer_doc.customer_primary_address = add_doc.name
        customer_doc.customer_primary_contact = contact_document.name
        customer_doc.save(ignore_permissions=True)

        create_response(200, "customer created successfully")
        return

    except Exception as e:
        frappe.log_error("Customer Creation from Mobile", frappe.get_traceback())
        create_response(406, "customer creation failed", e)

        return


@frappe.whitelist()
def get_customer_detail(customer_name):
    try:
        customer_detail = frappe.db.sql(
            """
		select c.name,c.customer_name,c.custom_date_of_birth,c.custom_anniversary_date,c.custom_sales_person,c.custom_client_tiers, c.custom_incognito,
		COALESCE(c.custom_contact, c.contact_no) AS mobile_no,c.email_id,c.customer_primary_address,(SELECT MAX(si.posting_date) FROM `tabSales Invoice` si WHERE si.customer = c.customer_name) AS last_purchase_date
		from `tabCustomer` c 
		where name = %(customer)s""",
            {"customer": customer_name},
            as_dict=1,
        )

        customer_detail[0]["primary_address"] = get_address_display(
            customer_detail[0]["customer_primary_address"]
        )

        active_campaigns = frappe.db.sql(
            """select td.name,td.reference_name,td.reference_type,td.custom_customer,td.status,cp.custom_start_date,custom_end_date,cp.description from `tabToDo` td inner join `tabCampaign` cp on td.reference_name = cp.name where td.custom_customer = %(customer)s and td.reference_type = 'Campaign' and cp.custom_enable = 1 and td.status = 'Open' """,
            {"customer": customer_name},
            as_dict=1,
        )

        customer_detail[0]["active_campaigns"] = active_campaigns

        if customer_detail:
            create_response(200, "Customer Fetched!", customer_detail[0])
            return
        else:
            create_response(
                406,
                "Customer data not found",
                "Customer data is incomplete or does not exist",
            )
            return
    except Exception as e:
        frappe.log_error("Customer Details Fetched Failed", frappe.get_traceback())
        create_response(406, "Internal server error", str(e))
        return


@frappe.whitelist()
def close_active_todo(todo_list):
    try:
        for todo in todo_list:
            frappe.db.sql(
                """update `tabToDo` set status = 'Closed' where name = %(todo)s""",
                {"todo": todo},
            )
        create_response(200, "Todo closed successfully")
        return
    except Exception as e:
        create_response(406, "Internal server error", str(e))
        return


@frappe.whitelist()
def sales_person_list(assigned=None):
    try:
        # If `assigned`, only return the current user's subtree
        if assigned:
            employee = frappe.db.get_value(
                "Employee", {"user_id": frappe.session.user}, "name"
            )
            if not employee:
                return create_response(406, "Employee not found for the current user.")

            sales_person, is_group = frappe.db.get_value(
                "Sales Person", {"employee": employee}, ["name", "is_group"]
            ) or (None, None)

            if not sales_person:
                return create_response(
                    406, "No Sales Person linked to your Employee record."
                )

            # If the current user's Sales Person is a group, return its descendants (unique)
            if is_group:
                descendants = get_decendants(sales_person, seen=set())
                return create_response(200, "Sales Person List Fetched!", descendants)
            else:
                # Not a group → no subordinates
                return create_response(200, "Sales Person List Fetched!", [])

        # Else: Get ALL sales persons (unique)
        rows = frappe.db.sql(
            """
            SELECT DISTINCT
                sp.name,
                sp.custom_botique,
                ep.cell_number,
                ep.prefered_email
            FROM `tabSales Person` sp
            LEFT JOIN `tabEmployee` ep ON sp.employee = ep.name
            WHERE sp.name NOT IN ('Sales Team')
            """,
            as_dict=1,
        )
        return create_response(200, "Sales Person List Fetched!", rows)

    except Exception as e:
        return create_response(
            406, "Internal server error", frappe.get_traceback() or str(e)
        )


def get_decendants(sales_person, seen=None):
    """Return all descendants of a Sales Person (unique by name)."""
    if seen is None:
        seen = set()

    result = []

    children = frappe.db.sql(
        """
        SELECT
            sp.is_group,
            sp.name,
            sp.custom_botique,
            ep.cell_number,
            ep.prefered_email
        FROM `tabSales Person` sp
        LEFT JOIN `tabEmployee` ep ON sp.employee = ep.name
        WHERE sp.name NOT IN ('Sales Team')
          AND sp.parent_sales_person = %(sales_person)s
        """,
        {"sales_person": sales_person},
        as_dict=1,
    )

    for child in children:
        child_name = child["name"]
        if child_name in seen:
            continue  # skip duplicates

        seen.add(child_name)
        result.append(child)

        # Recurse only for groups
        if child.get("is_group") == 1:
            result.extend(get_decendants(child_name, seen=seen))

    return result


@frappe.whitelist()
def update_customer_mobile(customer_name, mobile_number):
    try:
        frappe.db.sql(
            """
			UPDATE `tabContact Phone` AS cp
			LEFT JOIN `tabDynamic Link` AS link ON cp.parent = link.parent
			SET cp.phone = %(phone)s 
			WHERE cp.parenttype = 'Contact' 
			AND link.link_doctype = 'Customer'
			AND link.link_name = %(customer)s
		""",
            {"phone": mobile_number, "customer": customer_name},
        )

        frappe.db.sql(
            """
			UPDATE `tabContact` AS c
			INNER JOIN `tabDynamic Link` AS link ON c.name = link.parent
			SET c.mobile_no = %(phone)s 
			WHERE link.link_doctype = 'Customer'
			AND link.link_name = %(customer)s
		""",
            {"phone": mobile_number, "customer": customer_name},
        )

        customer = frappe.get_doc("Customer", customer_name)
        customer.custom_contact = mobile_number
        customer.save(ignore_permissions=1)
        frappe.db.commit()

        create_response(200, f"Mobile Number Updated For {customer_name}")
        return
    except Exception as e:
        create_response(406, "Mobile Number Updated Failed", str(e))
        return


@frappe.whitelist()
def get_all_customer_list():
    try:
        search = frappe.local.form_dict.search or ""
        offset = (
            int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0
        )

        condition = "AND customer_name LIKE %(search)s" if search else ""

        customer_list = frappe.db.sql(
            """
			SELECT customer_name, COALESCE(custom_contact, contact_no) AS mobile_no
			FROM `tabCustomer`
			WHERE disabled = 0 {conditions}
			LIMIT %(offset)s, 20
		""".format(conditions=condition),
            {"search": f"%{search}%", "offset": int(offset)},
            as_dict=True,
        )

        create_response(200, "Customer List Fetched.", customer_list)
        return

    except Exception as e:
        create_response(406, "Customer List Fetched Failed!", str(e))
        return


@frappe.whitelist()
def get_lead_source():
    try:
        search = frappe.local.form_dict.get("search", "") or ""
        offset = (
            int(frappe.local.form_dict.offset) if frappe.local.form_dict.offset else 0
        )

        condition = "WHERE name LIKE %(search)s" if search else ""
        lead_source_list = frappe.db.sql(
            """
			SELECT name 
			FROM `tabLead Source`
			{conditions}
			LIMIT %(offset)s, 20
		""".format(conditions=condition),
            {"search": f"%{search}%", "offset": offset},
            as_dict=True,
        )

        create_response(200, "Lead Source List Fetched.", lead_source_list)
        return
    except Exception as e:
        create_response(406, "Lead Source List Fetch Failed!", str(e))
        return
