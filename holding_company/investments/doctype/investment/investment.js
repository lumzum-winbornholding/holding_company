frappe.ui.form.on('Investment', {
	refresh: function(frm) {
		// Only disable save for manual creation (new records without investment_application)
		if (frm.doc.__islocal && !frm.doc.investment_application) {
			frm.disable_save();
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Investment records can only be created from Investment Application. Please use the "Create Investment" button in Investment Application form.'),
				indicator: 'red'
			});
		} else {
			// Enable save for records created from Investment Application
			frm.enable_save();
		}
	},
	
	investment_application: function(frm) {
		if (frm.doc.investment_application) {
			fetch_investment_application_data(frm);
		}
	},
	
	investment_amount: function(frm) {
		calculate_share_rate(frm);
	},
	
	no_of_shares: function(frm) {
		calculate_share_rate(frm);
	}
});

// List view indicator for custom_status field
frappe.listview_settings['Investment'] = {
	get_indicator: function(doc) {
		if (doc.custom_status === "Recovered") {
			return [__("Recovered"), "green", "custom_status,=,Recovered"];
		} else if (doc.custom_status === "Partially Recovered") {
			return [__("Partially Recovered"), "blue", "custom_status,=,Partially Recovered"];
		} else if (doc.custom_status === "Unrecovered") {
			return [__("Unrecovered"), "red", "custom_status,=,Unrecovered"];
		}
		return null;
	}
};

function calculate_share_rate(frm) {
	const investment_amount = flt(frm.doc.investment_amount);
	const no_of_shares = flt(frm.doc.no_of_shares);
	
	if (investment_amount && no_of_shares) {
		const share_rate = investment_amount / no_of_shares;
		frm.set_value('share_rate', share_rate);
	} else {
		frm.set_value('share_rate', 0);
	}
}

function fetch_investment_application_data(frm) {
	// Fetch data from Investment Application
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Investment Application',
			name: frm.doc.investment_application
		},
		callback: function(r) {
			if (r.message) {
				const ia_doc = r.message;
				
				// Map fields from Investment Application to Investment
				const field_mappings = {
					'investment_amount': 'investment_amount',
					'no_of_shares': 'no_of_shares',
					'share_rate': 'share_rate',
					'investee': 'investee',
					'company': 'company',
					'date': 'date',
					'investment_account': 'investment_account',
					'dividend_income_account': 'dividend_income_account',
					'bank_account': 'bank_account',
					'dividend_frequency': 'dividend_frequency',
					'purpose': 'purpose'
				};
				
				// Set values for each mapped field
				Object.keys(field_mappings).forEach(function(source_field) {
					const target_field = field_mappings[source_field];
					if (ia_doc[source_field] !== undefined && ia_doc[source_field] !== null) {
						frm.set_value(target_field, ia_doc[source_field]);
					}
				});
				
				// Calculate share rate if not fetched or fetch failed
				if (!frm.doc.share_rate || flt(frm.doc.share_rate) === 0) {
					calculate_share_rate(frm);
				}
				
				// Enable save button after data is fetched
				frm.enable_save();
				
				frappe.show_alert(__('Data fetched from Investment Application'), 3);
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Investment Application data: {0}', [err.message]));
			
			// Still calculate share rate in case of fetch error
			calculate_share_rate(frm);
		}
	});
}