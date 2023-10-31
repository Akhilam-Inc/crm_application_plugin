frappe.ui.form.on('Campaign', {
	refresh(frm) {
		// your code here

        frm.add_custom_button(__('Create Todo'), function(){

           frappe.call({
                method: 'crm_application_plugin.crm_application_plugin.overrides.campaign.create_todo',
                args: {
                    'self': frm.doc
                },
                freeze: true,
                callback: (r) => {
                    console.log(r.message)
                }
            })
        });

        frm.add_custom_button(__('Get Customers'), function(){

            if(frm.doc.custom_campaign_based_on == "Customer Type"){
                
                frappe.call({
                    method: 'crm_application_plugin.crm_application_plugin.overrides.campaign.create_todo',
                    args: {
                        'self': frm.doc
                    },
                    freeze: true,
                    callback: (r) => {
                        console.log(r.message)
                    }
                })
            }
            
         });
	}
})