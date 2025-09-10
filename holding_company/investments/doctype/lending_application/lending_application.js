frappe.ui.form.on('Lending Application', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			// Clear account fields when creating new record
			frm.set_value('loan_account', '');
			frm.set_value('interest_income_account', '');
			frm.set_value('bank_account', '');
		}
	},
	
	borrower: function(frm) {
		if (frm.doc.borrower && frm.doc.company) {
			fetch_borrower_accounts(frm);
		}
	},
	
	company: function(frm) {
		if (frm.doc.borrower && frm.doc.company) {
			fetch_borrower_accounts(frm);
		}
	}
});

function fetch_borrower_accounts(frm) {
	// First, get the Borrower document to access its child table
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Borrower',
			name: frm.doc.borrower
		},
		callback: function(r) {
			if (r.message && r.message.borrower_accounts) {
				// Find the account row that matches the company
				const company_accounts = r.message.borrower_accounts.find(
					account => account.company === frm.doc.company
				);
				
				if (company_accounts) {
					// Map the fields from Borrower Accounts to Lending Application
					const field_mappings = {
						'loans_account': 'loan_account',
						'interests_income_account': 'interest_income_account',
						'bank_account': 'bank_account'
					};
					
					// Set the values for each mapped field
					Object.keys(field_mappings).forEach(function(source_field) {
						const target_field = field_mappings[source_field];
						if (company_accounts[source_field]) {
							frm.set_value(target_field, company_accounts[source_field]);
						}
					});
					
					frappe.show_alert(__('Account fields updated from Borrower Accounts'), 3);
				} else {
					// Clear account fields if no matching company found
					frm.set_value('loan_account', '');
					frm.set_value('interest_income_account', '');
					frm.set_value('bank_account', '');
					
					frappe.msgprint(__('No Borrower Account found for company: {0}. Please configure accounts in the Borrower master.', [frm.doc.company]));
				}
			} else {
				// Clear account fields if no accounts found
				frm.set_value('loan_account', '');
				frm.set_value('interest_income_account', '');
				frm.set_value('bank_account', '');
				
				frappe.msgprint(__('No accounts configured for this Borrower. Please add accounts in the Borrower master.'));
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Borrower accounts: {0}', [err.message]));
		}
	});
}