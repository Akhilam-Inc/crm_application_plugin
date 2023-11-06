// Copyright (c) 2023, tailorraj and contributors
// For license information, please see license.txt

frappe.ui.form.on('Brand Training', {
	refresh: function(frm) {
		// your code here
	},
	validate:function(frm){
		var tbl = frm.doc.pdfs || [];
		var i = tbl.length;
		while (i--){
			if(!tbl[i].attach){
				frm.get_field("pdfs").grid.grid_rows[i].remove();
			}
		}
		frm.refresh();
		

		var tbl = frm.doc.videos || [];
		var i = tbl.length;
		while (i--){
			if(!tbl[i].file_url){
				frm.get_field("videos").grid.grid_rows[i].remove();
			}
		}
		frm.refresh();
	}
});
