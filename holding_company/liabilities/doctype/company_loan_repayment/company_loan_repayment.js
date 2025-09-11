frappe.ui.form.on('Company Loan Repayment', {
	refresh: function(frm) {
		// Clear journal_entry field (it will be auto-populated when created from Company Loan)
		if (frm.doc.__islocal) {
			frm.set_value('journal_entry', '');
		}
		
		// Only disable save if there's no company loan linked
		if (frm.doc.__islocal && !frm.doc.company_loan) {
			frm.disable_save();
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Company Loan Repayment records can only be created from Company Loan. Please use the "Create Repayment" button in Company Loan form.'),
				indicator: 'red'
			});
		}
		
		// Auto-calculate net amount when form loads
		frm.trigger('calculate_net_amount');
	},

	company_loan: function(frm) {
		if (frm.doc.company_loan) {
			// Fetch data from Company Loan
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Company Loan',
					name: frm.doc.company_loan
				},
				callback: function(r) {
					if (r.message) {
						const loan = r.message;
						
						// Map fields from Company Loan
						frm.set_value('lender', loan.lender);
						frm.set_value('company', loan.company);
						frm.set_value('liability_account', loan.liability_account);
						frm.set_value('interest_expense_account', loan.interest_expense_account);
						frm.set_value('bank_account', loan.bank_account);
						
						frappe.show_alert(__('Data fetched from Company Loan'), 3);
						
						// Show outstanding balance info
						if (loan.outstanding_balance) {
							frappe.show_alert(
								__('Outstanding Balance: {0}', [format_currency(loan.outstanding_balance)]), 
								5
							);
						}
					}
				}
			});
		}
	},

	repayment_amount: function(frm) {
		frm.trigger('calculate_net_amount');
	},

	repayment_interest: function(frm) {
		frm.trigger('calculate_net_amount');
	},

	calculate_net_amount: function(frm) {
		calculate_net_amount(frm);
	},

	validate: function(frm) {
		// Validate that repayment doesn't exceed outstanding balance
		if (frm.doc.company_loan && frm.doc.repayment_amount) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Company Loan',
					name: frm.doc.company_loan
				},
				callback: function(r) {
					if (r.message && r.message.outstanding_balance) {
						const outstanding = r.message.outstanding_balance;
						if (frm.doc.repayment_amount > outstanding) {
							frappe.msgprint({
								title: __('Warning'),
								message: __('Repayment amount ({0}) exceeds outstanding balance ({1})', 
									[format_currency(frm.doc.repayment_amount), format_currency(outstanding)]),
								indicator: 'orange'
							});
						}
					}
				}
			});
		}
	}
});

function calculate_net_amount(frm) {
	const repayment_amount = flt(frm.doc.repayment_amount);
	const repayment_interest = flt(frm.doc.repayment_interest);
	
	const net_amount = repayment_amount + repayment_interest;
	frm.set_value('net_amount', net_amount);
}