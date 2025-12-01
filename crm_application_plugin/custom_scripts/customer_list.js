frappe.listview_settings["Customer"] = {
	onload: function (listview) {
		listview.page.add_action_item(__("Mark Incognito"), () => {
			listview.call_for_selected_items(
				"crm_application_plugin.crm_application_plugin.overrides.customer.mark_incognito"
			);
		});
	},
};