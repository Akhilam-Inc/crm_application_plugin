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

                if(frm.doc.custom_campaign_based_on == "Customer Type" && frm.doc.custom_client_tiers){

                    frappe.call({
                        method: 'crm_application_plugin.crm_application_plugin.overrides.campaign.get_customer_by_tiers',
                        args: {
                            'client_tier': frm.doc.custom_client_tiers,
                            'sales_person':frm.doc.custom_sales_person
                        },
                        freeze: true,
                        callback: (r) => {
                            // console.log(r.message)
                            if (r.message.length > 0 ){
                                frm.clear_table('custom_customer_campaign_list_')
                                for(var i in r.message){
                                    let row = frm.add_child('custom_customer_campaign_list_', {
                                        "customer_name": r.message[i].name,
                                        "client_tiers": r.message[i].custom_client_tiers,
                                        "sales_person":r.message[i].custom_sales_person
                                    });
                                    
                                    frm.refresh_field('custom_customer_campaign_list_');
                                }
    
                            }
                            
                        }
                    })
                }

                if(frm.doc.custom_campaign_based_on === "Last Purchased" ){
                    
                    frappe.call({
                        method: 'crm_application_plugin.crm_application_plugin.overrides.campaign.get_sales_details',
                        args: {
                            'from_date': frm.doc.custom_from_date,
                            'to_date':frm.doc.custom_to_date
                        },
                        freeze: true,
                        callback: (r) => {
                            // console.log(r.message)
                            if (r.message.length > 0 ){
                                frm.clear_table('custom_customer_campaign_list_')
                                for(var i in r.message){
                                    let row = frm.add_child('custom_customer_campaign_list_', {
                                        "customer_name": r.message[i].name,
                                        "client_tiers": r.message[i].custom_client_tiers,
                                        "sales_person":r.message[i].custom_sales_person,
                                        "last_purchased":r.message[i].last_order_date
                                    });
                                    
                                    frm.refresh_field('custom_customer_campaign_list_');
                                }
                            }
                        }
                    })

                }

                if(frm.doc.custom_campaign_based_on === "Last Contacted"){
                    frappe.call({
                        method: 'crm_application_plugin.crm_application_plugin.overrides.campaign.get_last_contacted',
                        args: {
                            'from_date': frm.doc.custom_from_date,
                            'to_date':frm.doc.custom_to_date
                        },
                        freeze: true,
                        callback: (r) => {
                            // console.log(r.message)
                            if (r.message.length > 0 ){
                                frm.clear_table('custom_customer_campaign_list_')
                                for(var i in r.message){
                                    let row = frm.add_child('custom_customer_campaign_list_', {
                                        "customer_name": r.message[i].name,
                                        "client_tiers": r.message[i].custom_client_tiers,
                                        "sales_person":r.message[i].custom_sales_person
                                    });
                                    
                                    frm.refresh_field('custom_customer_campaign_list_');
                                }
                            }
                        }
                    })
                }
                
            });    
            
	}
})