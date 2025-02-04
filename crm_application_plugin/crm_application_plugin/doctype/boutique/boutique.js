// Copyright (c) 2023, tailorraj and contributors
// For license information, please see license.txt

frappe.ui.form.on('Boutique', {
	// refresh: function(frm) {

	// }
	boutique_location:function(frm){
		if(frm.doc.boutique_location){
			return frm.call({
			method: "frappe.contacts.doctype.address.address.get_address_display",
			args: {
				"address_dict": frm.doc.boutique_location
			},
			callback: function(r) {
				if(r.message)
					frm.set_value("boutique_location_display", r.message);
				}
			});
			  
		}
		else{
			frm.set_value("boutique_location_display", "");
		}
	}
});
