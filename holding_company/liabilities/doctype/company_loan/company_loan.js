frappe.ui.form.on('Company Loan', {
	refresh: function(frm) {
		// Only disable save if there's no company loan application linked
		if (frm.doc.__islocal && !frm.doc.company_loan_application) {
			frm.disable_save();
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Company Loan records can only be created from Company Loan Application. Please use the "Create Loan" button in Company Loan Application form.'),
				indicator: 'red'
			});
		}
		
	},

	company_loan_application: function(frm) {
		if (frm.doc.company_loan_application) {
			fetch_company_loan_application_data(frm);
		}
	}
});

// List view color indicators
frappe.listview_settings['Company Loan'] = {
	get_indicator: function(doc) {
		if (doc.custom_status === 'Repaid') {
			return [__('Repaid'), 'green', 'custom_status,=,Repaid'];
		} else if (doc.custom_status === 'Partially Repaid') {
			return [__('Partially Repaid'), 'blue', 'custom_status,=,Partially Repaid'];
		} else {
			return [__('Unpaid'), 'red', 'custom_status,=,Unpaid'];
		}
	}
};

function fetch_company_loan_application_data(frm) {
	// Fetch data from Company Loan Application
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Company Loan Application',
			name: frm.doc.company_loan_application
		},
		callback: function(r) {
			if (r.message) {
				const cla_doc = r.message;
				
				// Map fields from Company Loan Application to Company Loan
				const field_mappings = {
					'loan_amount': 'loan_amount',
					'interest_rate': 'interest_rate',
					'repayment_frequency': 'repayment_frequency',
					'purpose': 'purpose',
					'lender': 'lender',
					'company': 'company',
					'liability_account': 'liability_account',
					'interest_expense_account': 'interest_expense_account',
					'bank_account': 'bank_account'
				};
				
				// Set values for each mapped field
				Object.keys(field_mappings).forEach(function(source_field) {
					const target_field = field_mappings[source_field];
					if (cla_doc[source_field] !== undefined && cla_doc[source_field] !== null) {
						frm.set_value(target_field, cla_doc[source_field]);
					}
				});
				
				frappe.show_alert(__('Data fetched from Company Loan Application'), 3);
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Company Loan Application data: {0}', [err.message]));
		}
	});
}