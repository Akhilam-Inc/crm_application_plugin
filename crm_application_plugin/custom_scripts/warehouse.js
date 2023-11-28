frappe.ui.form.on('Warehouse', {
	refresh(frm) {
		// your code here


        frm.set_query("custom_reserved_warehouse", function() {
            return {
                "filters": {
                    "name": ["!=", frm.doc.name],
                    "is_group": 0,
                    "custom_is_reserved": 1
                }
            };
        }   );
		
	}
})