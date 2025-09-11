frappe.ui.form.on('Investment Application', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			// Clear account fields when creating new record
			frm.set_value('investment_account', '');
			frm.set_value('dividend_income_account', '');
			frm.set_value('bank_account', '');
		}
	},
	
	investee: function(frm) {
		if (frm.doc.investee && frm.doc.company) {
			fetch_investee_accounts(frm);
		}
	},
	
	company: function(frm) {
		if (frm.doc.investee && frm.doc.company) {
			fetch_investee_accounts(frm);
		}
	},
	
	investment_amount: function(frm) {
		calculate_share_rate(frm);
	},
	
	no_of_shares: function(frm) {
		calculate_share_rate(frm);
	}
});

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

function fetch_investee_accounts(frm) {
	// First, get the Investee document to access its child table
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Investee',
			name: frm.doc.investee
		},
		callback: function(r) {
			if (r.message && r.message.investee_accounts) {
				// Find the account row that matches the company
				const company_accounts = r.message.investee_accounts.find(
					account => account.company === frm.doc.company
				);
				
				if (company_accounts) {
					// Map the fields from Investee Accounts to Investment Application
					const field_mappings = {
						'investment_account': 'investment_account',
						'dividend_income_account': 'dividend_income_account',
						'bank_account': 'bank_account'
					};
					
					// Set the values for each mapped field
					Object.keys(field_mappings).forEach(function(source_field) {
						const target_field = field_mappings[source_field];
						if (company_accounts[source_field]) {
							frm.set_value(target_field, company_accounts[source_field]);
						}
					});
					
					frappe.show_alert(__('Account fields updated from Investee Accounts'), 3);
				} else {
					// Clear account fields if no matching company found
					frm.set_value('investment_account', '');
					frm.set_value('dividend_income_account', '');
					frm.set_value('bank_account', '');
					
					frappe.msgprint(__('No Investee Account found for company: {0}. Please configure accounts in the Investee master.', [frm.doc.company]));
				}
			} else {
				// Clear account fields if no accounts found
				frm.set_value('investment_account', '');
				frm.set_value('dividend_income_account', '');
				frm.set_value('bank_account', '');
				
				frappe.msgprint(__('No accounts configured for this Investee. Please add accounts in the Investee master.'));
			}
		},
		error: function(err) {
			frappe.msgprint(__('Error fetching Investee accounts: {0}', [err.message]));
		}
	});
}