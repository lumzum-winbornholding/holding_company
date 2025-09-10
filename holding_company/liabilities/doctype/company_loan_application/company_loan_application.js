frappe.ui.form.on('Company Loan Application', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			// Clear account fields when creating new record
			frm.set_value('liability_account', '');
			frm.set_value('interest_expense_account', '');
			frm.set_value('bank_account', '');
		}
	},
	
	lender: function(frm) {
		if (frm.doc.lender && frm.doc.company) {
			fetch_lender_accounts(frm);
		}
	},
	
	company: function(frm) {
		if (frm.doc.lender && frm.doc.company) {
			fetch_lender_accounts(frm);
		}
	}
});

function fetch_lender_accounts(frm) {
	// First, get the Lender document to access its child table
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Lender',
			name: frm.doc.lender
		},
		callback: function(r) {
			if (r.message && r.message.lender_accounts) {
				// Find the account row that matches the company
				const company_accounts = r.message.lender_accounts.find(
					account => account.company === frm.doc.company
				);
				
				if (company_accounts) {
					// Map the fields from Lender Accounts to Company Loan Application
					const field_mappings = {
						'liabilities_account': 'liability_account',
						'interests_expense_account': 'interest_expense_account',
						'bank_account': 'bank_account'
					};
					
					// Set the values for each mapped field
					Object.keys(field_mappings).forEach(function(source_field) {
						const target_field = field_mappings[source_field];
						if (company_accounts[source_field]) {
							frm.set_value(target_field, company_accounts[source_field]);
						}
					});
					
					frappe.show_alert(__('Account fields updated from Lender Accounts'), 3);
				} else {
					// Clear account fields if no matching company found
					frm.set_value('liability_account', '');
					frm.set_value('interest_expense_account', '');
					frm.set_value('bank_account', '');
					
					frappe.msgprint(__('No Lender Account found for company: {0}. Please configure accounts in the Lender master.', [frm.doc.company]));
				}
			} else {
				// Clear account fields if no accounts found
				frm.set_value('liability_account', '');
				frm.set_value('interest_expense_account', '');
				frm.set_value('bank_account', '');
				
				frappe.msgprint(__('No accounts configured for this Lender. Please add accounts in the Lender master.'));
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Lender accounts: {0}', [err.message]));
		}
	});
}