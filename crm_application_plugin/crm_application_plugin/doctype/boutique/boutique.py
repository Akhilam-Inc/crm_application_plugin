# Copyright (c) 2023, tailorraj and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Boutique(Document):
	def validate(self):
		self.assign_manager_role_and_workspace()

	def assign_manager_role_and_workspace(self):
		# Stop if no manager is assigned
		if not self.boutique_manager:
			return

		user = frappe.get_doc("User", self.boutique_manager)
		has_changes = False

		# 1. Assign Boutique Manager Role using frappe.get_roles
		if "Boutique Manager" not in frappe.get_roles(self.boutique_manager):
			user.append("roles", {
				"role": "Boutique Manager"
			})
			has_changes = True

		# 2. Set Default Workspace (Home Page)
		# Frappe requires the URL route of the workspace here.
		# "Day Opening & Closing" typically translates to "day-opening-closing".
		workspace_route = "Day Opening & Closing"
		
		if user.default_workspace != workspace_route:
			user.default_workspace = workspace_route
			has_changes = True

		# Save only if we actually made modifications
		if has_changes:
			user.save(ignore_permissions=True)