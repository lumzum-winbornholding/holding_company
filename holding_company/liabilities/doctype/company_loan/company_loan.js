frappe.ui.form.on('Company Loan', {
	refresh: function(frm) {
		// Prevent manual creation - must be created from Company Loan Application
		if (frm.doc.__islocal && !frm.doc.company_loan_application) {
			frappe.msgprint(__('Company Loan cannot be created manually. Please create through Company Loan Application.'));
			frappe.set_route('List', 'Company Loan Application');
			return;
		}
		
		// Auto-refresh after submit to update calculated fields
		if (frm.doc.docstatus === 1) {
			frm.trigger('calculate_outstanding');
		}
	},

	company_loan_application: function(frm) {
		if (frm.doc.company_loan_application) {
			// Fetch data from Company Loan Application
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Company Loan Application',
					name: frm.doc.company_loan_application
				},
				callback: function(r) {
					if (r.message) {
						const app = r.message;
						
						// Map fields from Company Loan Application
						frm.set_value('loan_amount', app.loan_amount);
						frm.set_value('interest_rate', app.interest_rate);
						frm.set_value('repayment_frequency', app.repayment_frequency);
						frm.set_value('purpose', app.purpose);
						
						// Copy other essential fields
						frm.set_value('lender', app.lender);
						frm.set_value('company', app.company);
						frm.set_value('liability_account', app.liability_account);
						frm.set_value('interest_expense_account', app.interest_expense_account);
						frm.set_value('bank_account', app.bank_account);
						
						frappe.show_alert(__('Data fetched from Company Loan Application'), 3);
					}
				}
			});
		}
	},

	loan_amount: function(frm) {
		frm.trigger('calculate_outstanding');
	},

	total_repaid: function(frm) {
		frm.trigger('calculate_outstanding');
	},

	calculate_outstanding: function(frm) {
		if (frm.doc.loan_amount && frm.doc.total_repaid !== undefined) {
			const outstanding = frm.doc.loan_amount - (frm.doc.total_repaid || 0);
			frm.set_value('outstanding_balance', outstanding);
			
			// Update loan status based on repayment
			let status = 'Unpaid';
			if (frm.doc.total_repaid === 0) {
				status = 'Unpaid';
			} else if (frm.doc.total_repaid > 0 && outstanding > 0) {
				status = 'Partially Repaid';
			} else if (outstanding <= 0) {
				status = 'Repaid';
			}
			
			frm.set_value('custom_status', status);
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