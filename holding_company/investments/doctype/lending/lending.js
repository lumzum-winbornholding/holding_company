frappe.ui.form.on('Lending', {
	refresh: function(frm) {
		// Disable creation of new records manually
		frm.disable_save();
		
		if (frm.doc.__islocal && !frm.doc.lending_application) {
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Lending records can only be created from Lending Application. Please use the "Create Lending" button in Lending Application form.'),
				indicator: 'red'
			});
		}
	},
	
	lending_application: function(frm) {
		if (frm.doc.lending_application) {
			fetch_lending_application_data(frm);
		}
	}
});

// List view indicator for custom_status field
frappe.listview_settings['Lending'] = {
	get_indicator: function(doc) {
		if (doc.custom_status === "Repaid") {
			return [__("Repaid"), "green", "custom_status,=,Repaid"];
		} else if (doc.custom_status === "Partially Repaid") {
			return [__("Partially Repaid"), "blue", "custom_status,=,Partially Repaid"];
		} else if (doc.custom_status === "Unpaid") {
			return [__("Unpaid"), "red", "custom_status,=,Unpaid"];
		}
		return null;
	}
};

function fetch_lending_application_data(frm) {
	// Fetch data from Lending Application
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Lending Application',
			name: frm.doc.lending_application
		},
		callback: function(r) {
			if (r.message) {
				const la_doc = r.message;
				
				// Map fields from Lending Application to Lending
				const field_mappings = {
					'loan_amount': 'loan_amount',
					'interest_rate': 'interest_rate',
					'repayment_frequency': 'repayment_frequency',
					'purpose': 'purpose',
					'borrower': 'borrower',
					'company': 'company',
					'date': 'date',
					'loan_account': 'loan_account',
					'interest_income_account': 'interest_income_account',
					'bank_account': 'bank_account'
				};
				
				// Set values for each mapped field
				Object.keys(field_mappings).forEach(function(source_field) {
					const target_field = field_mappings[source_field];
					if (la_doc[source_field] !== undefined && la_doc[source_field] !== null) {
						frm.set_value(target_field, la_doc[source_field]);
					}
				});
				
				frappe.show_alert(__('Data fetched from Lending Application'), 3);
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Lending Application data: {0}', [err.message]));
		}
	});
}