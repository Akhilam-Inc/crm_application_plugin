import frappe
from crm_application_plugin.api.utils import create_response
from frappe.utils import add_months, get_first_day, get_last_day, getdate, today

# @frappe.whitelist()
# def target():
#     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#     if not employee:
#         create_response(406, "Employee not found")
#         return
#     sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
#     if not sales_person:
#         create_response(406, "Sales Person not found")
#         return
#     sales_persons = frappe.local.form_dict.sales_persons or ""
#     get_current_month = frappe.utils.data.getdate(frappe.utils.data.nowdate()).strftime(
#         "%B"
#     )
#     active_fiscal_year = frappe.db.get_value(
#         "Fiscal Year",
#         {
#             "year_start_date": ["<=", frappe.utils.data.nowdate()],
#             "year_end_date": [">=", frappe.utils.data.nowdate()],
#             "disabled": 0,
#         },
#         "name",
#     )
#     target_for_current_month = get_target(
#         [sales_person] + sales_persons.split(","), get_current_month, active_fiscal_year
#     )
#     target = target_for_current_month[0].tg_amt if target_for_current_month else 0
#     create_response(200, "Success", {"target": target})
#     return
# # @frappe.whitelist()
# # def achvievement():
# #     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
# #     if not employee:
# #         create_response(406,"Employee not found")
# #         return
# #     sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
# #     if not sales_person:
# #         create_response(406,"Sales Person not found")
# #         return
# #     sales_persons = frappe.local.form_dict.sales_persons or ""
# #     sales_target_achieved_for_current_month = get_achived([sales_person] + sales_persons.split(","))
# #     achieved = sales_target_achieved_for_current_month[0]['sales'] if sales_target_achieved_for_current_month else 0
# #     response_data = {
# #         "achvievement": achieved,
# #         "unit_per_transaction":sales_target_achieved_for_current_month[0]['unit_per_trans'] if sales_target_achieved_for_current_month else 0,
# #         "avg_amt_per_invoice":sales_target_achieved_for_current_month[0]['avg_amt_per_invoice'] if sales_target_achieved_for_current_month else 0
# #     }
# #     create_response(200,"Success",response_data)
# #     return
# @frappe.whitelist()
# def achvievement():
#     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#     if not employee:
#         create_response(406, "Employee not found")
#         return
#     sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
#     if not sales_person:
#         create_response(406, "Sales Person not found")
#         return
#     sales_persons = frappe.local.form_dict.sales_persons or ""
#     # build list once so we can reuse it
#     extra_sales_persons = sales_persons.split(",") if sales_persons else []
#     sales_person_list = [sales_person] + extra_sales_persons
#     sales_target_achieved_for_current_month = get_achived(sales_person_list)
#     achieved = (
#         sales_target_achieved_for_current_month[0]["sales"]
#         if sales_target_achieved_for_current_month
#         else 0
#     )
#     # keep originals as they are now
#     unit_per_transaction = (
#         sales_target_achieved_for_current_month[0]["unit_per_trans"]
#         if sales_target_achieved_for_current_month
#         else 0
#     )
#     avg_amt_per_invoice = (
#         sales_target_achieved_for_current_month[0]["avg_amt_per_invoice"]
#         if sales_target_achieved_for_current_month
#         else 0
#     )
#     # 🔹 NEW: get Watch qty
#     watch_qty = get_watch_qty_for_sales_persons(sales_person_list)
#     # divide totals by Watch qty (with zero safety)
#     if watch_qty:
#         unit_per_transaction = unit_per_transaction / watch_qty
#         avg_amt_per_invoice = avg_amt_per_invoice / watch_qty
#     else:
#         unit_per_transaction = 0
#         avg_amt_per_invoice = 0
#     response_data = {
#         "achvievement": achieved,
#         "unit_per_transaction": unit_per_transaction,
#         "avg_amt_per_invoice": avg_amt_per_invoice,
#     }
#     create_response(200, "Success", response_data)
#     return
# def get_target(sales_person_list, month, fiscal_year):
#     target_for_current_month = frappe.db.sql(
#         """
#     select td.name, td.target_amount, td.distribution_id, mdp.month, mdp.percentage_allocation, (sum(td.target_amount) * mdp.percentage_allocation) / 100 as tg_amt
#     from `tabTarget Detail` td
#     inner join `tabMonthly Distribution Percentage` mdp on td.distribution_id = mdp.parent
#     where td.parent IN %(sales_person_list)s and td.fiscal_year = %(fiscal_year)s and mdp.month = %(month)s group by mdp.month
#     """,
#         {
#             "sales_person_list": sales_person_list,
#             "fiscal_year": fiscal_year,
#             "month": month,
#         },
#         as_dict=1,
#     )
#     return target_for_current_month
# def get_achived(sales_person_list):
#     sales_target_achieved_for_current_month = frappe.db.sql(
#         """
#     select sum(sii.amount) as sales,count(si.name) as si_count,sum(sii.qty) as itm_qty,sum(sii.qty)/count(si.name) as unit_per_trans,sum(sii.amount)/count(si.name) as avg_amt_per_invoice  from `tabSales Invoice Item` sii inner join `tabSales Invoice` si on sii.parent = si.name where si.docstatus = 1 and sii.sales_person IN %(sales_person_list)s and month(si.posting_date) = month(now()) and year(si.posting_date) = year(now()) group by month(si.posting_date),year(si.posting_date)""",
#         {"sales_person_list": sales_person_list},
#         as_dict=1,
#     )
#     return sales_target_achieved_for_current_month
# @frappe.whitelist()
# def botique_target():
#     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#     if not employee:
#         create_response(406, "Employee not found")
#         return
#     sales_person_botique = frappe.db.get_value(
#         "Sales Person", {"employee": employee}, "custom_botique"
#     )
#     if not sales_person_botique:
#         create_response(406, "Botique not found")
#         return
#     botiques = frappe.local.form_dict.botiques or ""
#     botiue_sales_person_list = frappe.db.get_all(
#         "Sales Person",
#         {"custom_botique": ["IN", [sales_person_botique] + botiques.split(",")]},
#         "name",
#         pluck="name",
#     )
#     get_current_month = frappe.utils.data.getdate(frappe.utils.data.nowdate()).strftime(
#         "%B"
#     )
#     active_fiscal_year = frappe.db.get_value(
#         "Fiscal Year",
#         {
#             "year_start_date": ["<=", frappe.utils.data.nowdate()],
#             "year_end_date": [">=", frappe.utils.data.nowdate()],
#             "disabled": 0,
#         },
#         "name",
#     )
#     target_for_current_month = get_target(
#         botiue_sales_person_list, get_current_month, active_fiscal_year
#     )
#     target = target_for_current_month[0].tg_amt if target_for_current_month else 0
#     create_response(200, "Success", {"target": target})
#     return
# # @frappe.whitelist()
# # def botique_achvievement():
# #     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
# #     if not employee:
# #         create_response(406,"Employee not found")
# #         return
# #     sales_person_botique = frappe.db.get_value("Sales Person", {"employee": employee}, "custom_botique")
# #     if not sales_person_botique:
# #         create_response(406,"Botique not found")
# #         return
# #     botiques = frappe.local.form_dict.botiques or ""
# #     botiue_sales_person_list = frappe.db.get_all("Sales Person", {"custom_botique": ["IN" , [sales_person_botique] + botiques.split(",")]}, "name",pluck="name")
# #     sales_target_achieved_for_current_month = get_achived(botiue_sales_person_list)
# #     # achieved = sales_target_achieved_for_current_month[0]['sales'] if sales_target_achieved_for_current_month else 0
# #     sales_target_achieved_for_current_month_by_cost_center = boutique_achievement_by_cost_center([sales_person_botique] + botiques.split(","))
# #     achieved = sales_target_achieved_for_current_month_by_cost_center if sales_target_achieved_for_current_month_by_cost_center else 0
# #     response_data = {
# #         "achvievement": achieved,
# #         "unit_per_transaction":sales_target_achieved_for_current_month[0]['unit_per_trans'] if sales_target_achieved_for_current_month else 0,
# #         "avg_amt_per_invoice":sales_target_achieved_for_current_month[0]['avg_amt_per_invoice'] if sales_target_achieved_for_current_month else 0
# #     }
# #     create_response(200,"Success",response_data)
# #     return
# @frappe.whitelist()
# def botique_achvievement():
#     employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
#     if not employee:
#         create_response(406, "Employee not found")
#         return
#     sales_person_botique = frappe.db.get_value(
#         "Sales Person", {"employee": employee}, "custom_botique"
#     )
#     if not sales_person_botique:
#         create_response(406, "Botique not found")
#         return
#     botiques = frappe.local.form_dict.botiques or ""
#     botiue_sales_person_list = frappe.db.get_all(
#         "Sales Person",
#         {"custom_botique": ["IN", [sales_person_botique] + botiques.split(",")]},
#         "name",
#         pluck="name",
#     )
#     sales_target_achieved_for_current_month = get_achived(botiue_sales_person_list)
#     sales_target_achieved_for_current_month_by_cost_center = (
#         boutique_achievement_by_cost_center(
#             [sales_person_botique] + botiques.split(",")
#         )
#     )
#     achieved = (
#         sales_target_achieved_for_current_month_by_cost_center
#         if sales_target_achieved_for_current_month_by_cost_center
#         else 0
#     )
#     # keep existing totals
#     unit_per_transaction = (
#         sales_target_achieved_for_current_month[0]["unit_per_trans"]
#         if sales_target_achieved_for_current_month
#         else 0
#     )
#     avg_amt_per_invoice = (
#         sales_target_achieved_for_current_month[0]["avg_amt_per_invoice"]
#         if sales_target_achieved_for_current_month
#         else 0
#     )
#     # 🔹 NEW: Watch qty for all sales persons under the selected boutiques
#     watch_qty = get_watch_qty_for_sales_persons(botiue_sales_person_list)
#     if watch_qty:
#         unit_per_transaction = unit_per_transaction / watch_qty
#         avg_amt_per_invoice = avg_amt_per_invoice / watch_qty
#     else:
#         unit_per_transaction = 0
#         avg_amt_per_invoice = 0
#     response_data = {
#         "achvievement": achieved,
#         "unit_per_transaction": unit_per_transaction,
#         "avg_amt_per_invoice": avg_amt_per_invoice,
#         "watch_qty": watch_qty,
#     }
#     create_response(200, "Success", response_data)
#     return
# def boutique_achievement_by_cost_center(boutiques):
#     """
#     boutiques: list of Boutique names (or a comma-separated string).
#     Sums achievement for ALL boutiques' cost centers.
#     """
#     if isinstance(boutiques, str):
#         boutiques = [b.strip() for b in boutiques.split(",") if b.strip()]
#     if not boutiques:
#         return 0
#     # get all cost centers mapped to these boutiques
#     cost_centers = frappe.get_all(
#         "Boutique",
#         filters={"name": ["in", boutiques]},
#         pluck="boutique_cost_center",
#     )
#     cost_centers = [c for c in cost_centers if c]
#     if not cost_centers:
#         return 0
#     first_day_of_month = get_first_day(today())
#     last_day_of_month = get_last_day(today())
#     result = frappe.db.sql(
#         """
#         SELECT COALESCE(SUM(sii.amount), 0) AS total_amount
#         FROM `tabSales Invoice Item` sii
#         INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
#         WHERE
#             si.docstatus = 1
#             AND sii.cost_center IN %(cost_centers)s
#             AND si.posting_date BETWEEN %(start_date)s AND %(end_date)s
#         """,
#         {
#             "cost_centers": tuple(cost_centers),
#             "start_date": first_day_of_month,
#             "end_date": last_day_of_month,
#         },
#         as_dict=1,
#     )
#     return result[0].total_amount if result else 0
# def get_watch_qty_for_sales_persons(sales_person_list):
#     """Total qty of sold items in Watch category for given sales persons (current month)."""
#     watch_qty_data = frappe.db.sql(
#         """
#         SELECT
#             COALESCE(SUM(sii.qty), 0) AS watch_qty
#         FROM `tabSales Invoice Item` sii
#         INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
#         INNER JOIN `tabItem` i ON i.name = sii.item_code
#         WHERE
#             si.docstatus = 1
#             AND sii.sales_person IN %(sales_person_list)s
#             AND i.item_group = 'Watch'
#             AND MONTH(si.posting_date) = MONTH(CURDATE())
#             AND YEAR(si.posting_date) = YEAR(CURDATE())
#     """,
#         {"sales_person_list": sales_person_list},
#         as_dict=1,
#     )
#     return watch_qty_data[0]["watch_qty"] if watch_qty_data else 0


@frappe.whitelist()
def target():
    """Fetches sales target for a date range (defaults to current month)."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406, "Employee not found")
        return

    sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
    if not sales_person:
        create_response(406, "Sales Person not found")
        return

    # --- Range Parsing (Defaults to current month for both if missing) ---
    from_param = frappe.local.form_dict.get("from")
    to_param = frappe.local.form_dict.get("to")
    start_date, end_date = parse_range(from_param, to_param)

    sales_persons = frappe.local.form_dict.sales_persons or ""
    if sales_persons:
        sp_list = sales_persons.split(",")
    else:
        sp_list = [sales_person]

    total_target = 0
    current_iter = start_date

    # Iterate through months in the range to accumulate target amounts
    while current_iter <= end_date:
        month_name = current_iter.strftime("%B")
        fiscal_year = frappe.db.get_value(
            "Fiscal Year",
            {
                "year_start_date": ["<=", current_iter],
                "year_end_date": [">=", current_iter],
                "disabled": 0,
            },
            "name",
        )
        if fiscal_year:
            target_res = get_target_sql(sp_list, month_name, fiscal_year)
            total_target += target_res[0].tg_amt if target_res else 0

        current_iter = add_months(current_iter, 1)

    frappe.log_error(
        title="KPI Debug: Target Range",
        message={
            "params": {"from": from_param, "to": to_param},
            "derived_range": {"start": str(start_date), "end": str(end_date)},
            "sales_persons": sp_list,
            "total_target": total_target,
        },
    )

    create_response(200, "Success", {"target": total_target})
    return


@frappe.whitelist()
def achvievement():
    """Calculates achievement KPIs and returns them along with the Watch quantity."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406, "Employee not found")
        return

    sales_person = frappe.db.get_value("Sales Person", {"employee": employee}, "name")
    if not sales_person:
        create_response(406, "Sales Person not found")
        return

    # --- Range Parsing ---
    # Defaults to current month for both if params are missing
    start_date, end_date = parse_range(
        frappe.local.form_dict.get("from"), frappe.local.form_dict.get("to")
    )

    sales_persons = frappe.local.form_dict.sales_persons or ""
    if sales_persons:
        sp_list = sales_persons.split(",")
    else:
        sp_list = [sales_person]

    # Fetch metrics and watch quantity for the specific item group 'Watch'
    sales_data = get_achived_range_sql(sp_list, start_date, end_date)
    watch_qty = get_watch_qty_range_sql(sp_list, start_date, end_date)

    achieved = sales_data[0]["sales"] if sales_data else 0
    unit_per_trans = sales_data[0]["unit_per_trans"] if sales_data else 0
    avg_amt_inv = sales_data[0]["avg_amt_per_invoice"] if sales_data else 0

    # Debug Log for the specific range and results
    frappe.log_error(
        title="KPI Debug: Achievement Range with Qty",
        message={
            "range": [str(start_date), str(end_date)],
            "watch_qty": watch_qty,
            "total_sales": achieved,
            "sp_list": sp_list,
        },
    )

    # Normalize metrics based on Watch quantity
    if watch_qty:
        unit_per_trans = unit_per_trans / watch_qty
        avg_amt_inv = avg_amt_inv / watch_qty
    else:
        unit_per_trans = 0
        avg_amt_inv = 0

    # Updated response data including watch_qty
    response_data = {
        "achvievement": achieved,
        "unit_per_transaction": unit_per_trans,
        "avg_amt_per_invoice": avg_amt_inv,
        "watch_qty": watch_qty,
    }

    create_response(200, "Success", response_data)
    return


@frappe.whitelist()
def botique_target():
    """Fetches total sales target for one or more boutiques over a date range."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406, "Employee not found")
        return

    # Get the primary boutique of the logged-in user
    sales_person_botique = frappe.db.get_value(
        "Sales Person", {"employee": employee}, "custom_botique"
    )
    if not sales_person_botique:
        create_response(406, "Boutique not found for this user")
        return

    # --- Range Parsing ---
    from_param = frappe.local.form_dict.get("from")
    to_param = frappe.local.form_dict.get("to")
    start_date, end_date = parse_range(from_param, to_param)

    # Get additional boutiques from form dict if provided
    botiques_input = frappe.local.form_dict.get("botiques") or ""

    if botiques_input:
        bt_list = botiques_input.split(",")
    else:
        bt_list = [sales_person_botique]

    # Find all Sales Persons associated with the selected boutiques
    botiue_sales_person_list = frappe.db.get_all(
        "Sales Person",
        {"custom_botique": ["IN", bt_list]},
        pluck="name",
    )

    if not botiue_sales_person_list:
        frappe.log_error(
            title="KPI Debug: Boutique Target Error",
            message=f"No sales persons found for boutiques: {bt_list}",
        )
        create_response(
            200, "No sales persons found for selected boutiques", {"target": 0}
        )
        return

    total_target = 0
    current_iter = start_date

    # Iterate through months in the range to accumulate target amounts
    while current_iter <= end_date:
        month_name = current_iter.strftime("%B")

        # Determine the Fiscal Year for the current month in the iteration
        active_fiscal_year = frappe.db.get_value(
            "Fiscal Year",
            {
                "year_start_date": ["<=", current_iter],
                "year_end_date": [">=", current_iter],
                "disabled": 0,
            },
            "name",
        )

        if active_fiscal_year:
            target_res = get_target_sql(
                botiue_sales_person_list, month_name, active_fiscal_year
            )
            total_target += target_res[0].tg_amt if target_res else 0

        current_iter = add_months(current_iter, 1)

    # Debug Log
    frappe.log_error(
        title="KPI Debug: Boutique Target Range",
        message={
            "input_boutiques": bt_list,
            "resolved_sales_persons": botiue_sales_person_list,
            "range": {"start": str(start_date), "end": str(end_date)},
            "total_accumulated_target": total_target,
        },
    )

    return create_response(200, "Success", {"target": total_target})


@frappe.whitelist()
def botique_achvievement():
    """Boutique achievement using Cost Centers for a date range."""
    employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
    if not employee:
        create_response(406, "Employee not found")
        return

    boutique_name = frappe.db.get_value(
        "Sales Person", {"employee": employee}, "custom_botique"
    )
    if not boutique_name:
        create_response(406, "Boutique not found")
        return

    # --- Range Parsing ---
    start_date, end_date = parse_range(
        frappe.local.form_dict.get("from"), frappe.local.form_dict.get("to")
    )

    extra_bts = frappe.local.form_dict.botiques or ""
    if extra_bts:
        bt_list = extra_bts.split(",")
    else:
        bt_list = [boutique_name]

    # Get all sales persons for these boutiques
    sp_list = frappe.db.get_all(
        "Sales Person", {"custom_botique": ["IN", bt_list]}, pluck="name"
    )

    achieved = get_boutique_cc_achievement_sql(bt_list, start_date, end_date)
    sales_metrics = get_achived_range_sql(sp_list, start_date, end_date)
    watch_qty = get_watch_qty_range_sql(sp_list, start_date, end_date)

    unit_per_trans = sales_metrics[0]["unit_per_trans"] if sales_metrics else 0
    avg_amt_inv = sales_metrics[0]["avg_amt_per_invoice"] if sales_metrics else 0

    frappe.log_error(
        title="KPI Debug: Boutique Range",
        message={
            "boutiques": bt_list,
            "cost_center_sales": achieved,
            "watch_qty": watch_qty,
            "dates": [str(start_date), str(end_date)],
        },
    )

    if watch_qty:
        unit_per_trans = unit_per_trans / watch_qty
        avg_amt_inv = avg_amt_inv / watch_qty
    else:
        unit_per_trans = 0
        avg_amt_inv = 0

    create_response(
        200,
        "Success",
        {
            "achvievement": achieved,
            "unit_per_transaction": unit_per_trans,
            "avg_amt_per_invoice": avg_amt_inv,
            "watch_qty": watch_qty,
        },
    )
    return


# --- Core Helper Functions ---


def parse_range(from_str, to_str):
    """
    Returns (start_date, end_date).
    If neither is passed, both default to current month/year.
    """
    current_date = getdate(today())

    def parse_part(p_str, is_start=True):
        if p_str and "-" in p_str:
            try:
                m, y = p_str.split("-")
                dt = f"{y}-{m}-01"
                return get_first_day(dt) if is_start else get_last_day(dt)
            except Exception:
                pass
        return get_first_day(current_date) if is_start else get_last_day(current_date)

    return parse_part(from_str, True), parse_part(to_str, False)


def get_target_sql(sp_list, month_name, fiscal_year):
    return frappe.db.sql(
        """
        SELECT (SUM(td.target_amount) * mdp.percentage_allocation) / 100 AS tg_amt 
        FROM `tabTarget Detail` td 
        INNER JOIN `tabMonthly Distribution Percentage` mdp ON td.distribution_id = mdp.parent  
        WHERE td.parent IN %(sp_list)s 
            AND td.fiscal_year = %(fy)s 
            AND mdp.month = %(m_name)s 
        GROUP BY mdp.month
        """,
        {"sp_list": sp_list, "fy": fiscal_year, "m_name": month_name},
        as_dict=1,
    )


def get_achived_range_sql(sp_list, start, end):
    return frappe.db.sql(
        """
        SELECT 
            SUM(sii.amount) AS sales, 
            COUNT(DISTINCT si.name) AS si_count, 
            SUM(sii.qty) AS itm_qty, 
            SUM(sii.qty)/NULLIF(COUNT(DISTINCT si.name), 0) AS unit_per_trans, 
            SUM(sii.amount)/NULLIF(COUNT(DISTINCT si.name), 0) AS avg_amt_per_invoice  
        FROM `tabSales Invoice Item` sii 
        INNER JOIN `tabSales Invoice` si ON sii.parent = si.name 
        WHERE si.docstatus = 1 
            AND sii.sales_person IN %(sp_list)s 
            AND si.posting_date BETWEEN %(start)s AND %(end)s
        """,
        {"sp_list": sp_list, "start": start, "end": end},
        as_dict=1,
    )


def get_boutique_cc_achievement_sql(boutiques, start, end):
    cc_list = frappe.get_all(
        "Boutique", filters={"name": ["in", boutiques]}, pluck="boutique_cost_center"
    )
    cc_list = [c for c in cc_list if c]

    if not cc_list:
        return 0

    res = frappe.db.sql(
        """
        SELECT COALESCE(SUM(sii.amount), 0) AS total
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
            AND sii.cost_center IN %(cc_list)s
            AND si.posting_date BETWEEN %(start)s AND %(end)s
        """,
        {"cc_list": tuple(cc_list), "start": start, "end": end},
        as_dict=1,
    )
    return res[0].total if res else 0


def get_watch_qty_range_sql(sp_list, start, end):
    res = frappe.db.sql(
        """
        SELECT COALESCE(SUM(sii.qty), 0) AS watch_qty
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
        INNER JOIN `tabItem` i ON i.name = sii.item_code
        WHERE si.docstatus = 1
            AND sii.sales_person IN %(sp_list)s
            AND i.item_group = 'Watch'
            AND si.posting_date BETWEEN %(start)s AND %(end)s
        """,
        {"sp_list": sp_list, "start": start, "end": end},
        as_dict=1,
    )
    return res[0]["watch_qty"] if res else 0
