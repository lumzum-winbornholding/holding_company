frappe.ui.form.on('Investment Return', {
	refresh: function(frm) {
		// Clear journal_entry field (it will be auto-populated when created from Investment)
		if (frm.doc.__islocal) {
			frm.set_value('journal_entry', '');
		}
		
		// Only disable save for manual creation (new records without investment)
		if (frm.doc.__islocal && !frm.doc.investment) {
			frm.disable_save();
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Investment Return records can only be created from Investment DocType. Please use the "Create Investment Return" button in Investment form.'),
				indicator: 'red'
			});
		} else {
			// Enable save for records created from Investment
			frm.enable_save();
		}
	},
	
	investment: function(frm) {
		if (frm.doc.investment) {
			fetch_investment_data(frm);
		}
	}
});

function fetch_investment_data(frm) {
	// Fetch data from Investment
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Investment',
			name: frm.doc.investment
		},
		callback: function(r) {
			if (r.message) {
				const investment_doc = r.message;
				
				// Map fields from Investment to Investment Return
				const field_mappings = {
					'investee': 'investee',
					'company': 'company',
					'dividend_income_account': 'dividend_income_account',
					'bank_account': 'bank_account'
				};
				
				// Set values for each mapped field
				Object.keys(field_mappings).forEach(function(source_field) {
					const target_field = field_mappings[source_field];
					if (investment_doc[source_field] !== undefined && investment_doc[source_field] !== null) {
						frm.set_value(target_field, investment_doc[source_field]);
					}
				});
				
				// Enable save button after data is fetched
				frm.enable_save();
				
				frappe.show_alert(__('Data fetched from Investment'), 3);
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Investment data: {0}', [err.message]));
		}
	});
}