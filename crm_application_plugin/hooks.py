from . import __version__ as app_version

app_name = "crm_application_plugin"
app_title = "Crm Application Plugin"
app_publisher = "tailorraj"
app_description = "plugin for crm applications"
app_email = "tailorraj111@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/crm_application_plugin/css/crm_application_plugin.css"
# app_include_js = "/assets/crm_application_plugin/js/crm_application_plugin.js"

# include js, css files in header of web template
# web_include_css = "/assets/crm_application_plugin/css/crm_application_plugin.css"
# web_include_js = "/assets/crm_application_plugin/js/crm_application_plugin.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "crm_application_plugin/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "Campaign" : "custom_scripts/campaign.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }
fixtures = [

	{"dt": "Custom Field", "filters": [
		[
			"name", "in", [
				"Customer-custom_date_of_birth","Customer-custom_anniversary_date","Campaign-custom_start_date","Campaign-custom_end_date","Campaign-custom_column_break_tno0a",
                "Campaign-custom_campaign_based_on","Campaign-custom_customer_type","Campaign-custom_last_purchased","Campaign-custom_last_contacted","Campaign-custom_customer_campaign_list_",
                "Customer-custom_boutique","ToDo-custom_customer","Item-custom_product_details","Item-custom_reference","Item-custom_collection","Item-custom_dial_size","Item-custom_dial_shape",
                "Item-custom_case_material","Item-custom_column_break_dhzcs","Item-custom_diamonds","Item-custom_strap_bracelet","Item-custom_gender","Item-custom_movement","Item-custom_water_resistance",
                "Item-custom_brand_warranty","Campaign-custom_client_tiers","Customer-custom_sales_person","Customer-custom_client_tiers"
			]
		]
	]},
	
]

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "crm_application_plugin.utils.jinja_methods",
#	"filters": "crm_application_plugin.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "crm_application_plugin.install.before_install"
# after_install = "crm_application_plugin.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "crm_application_plugin.uninstall.before_uninstall"
# after_uninstall = "crm_application_plugin.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "crm_application_plugin.utils.before_app_install"
# after_app_install = "crm_application_plugin.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "crm_application_plugin.utils.before_app_uninstall"
# after_app_uninstall = "crm_application_plugin.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "crm_application_plugin.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"crm_application_plugin.tasks.all"
#	],
#	"daily": [
#		"crm_application_plugin.tasks.daily"
#	],
#	"hourly": [
#		"crm_application_plugin.tasks.hourly"
#	],
#	"weekly": [
#		"crm_application_plugin.tasks.weekly"
#	],
#	"monthly": [
#		"crm_application_plugin.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "crm_application_plugin.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "crm_application_plugin.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "crm_application_plugin.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["crm_application_plugin.utils.before_request"]
# after_request = ["crm_application_plugin.utils.after_request"]

# Job Events
# ----------
# before_job = ["crm_application_plugin.utils.before_job"]
# after_job = ["crm_application_plugin.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"crm_application_plugin.auth.validate"
# ]
