frappe.ui.form.on('Funds Hold', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1 && frm.doc.journal_entry) {
			frm.add_custom_button(__('View Journal Entry'), function() {
				frappe.set_route('Form', 'Journal Entry', frm.doc.journal_entry);
			}, __('Actions'));
		}
		
		// Set filters for linked documents
		frm.set_query('sales_invoice', function() {
			return {
				filters: {
					'company': frm.doc.company,
					'docstatus': 1
				}
			};
		});
		
		frm.set_query('payment_entry', function() {
			return {
				filters: {
					'reference_name': frm.doc.sales_invoice,
					'docstatus': 1,
					'payment_type': 'Receive'
				}
			};
		});
	},
	
	company: function(frm) {
		if (frm.doc.company) {
			// Set company abbr
			frappe.db.get_value('Company', frm.doc.company, 'abbr').then(r => {
				if (r.message) {
					frm.set_value('custom_company_abbr', r.message.abbr);
				}
			});
			
			// Set account filters and fetch default accounts
			set_account_filters(frm);
			fetch_default_accounts(frm);
		}
	},
	
	sales_invoice: function(frm) {
		if (frm.doc.sales_invoice) {
			// Clear payment entry when sales invoice changes
			frm.set_value('payment_entry', '');
			
			// Set payment entry filter
			frm.set_query('payment_entry', function() {
				return {
					filters: {
						'reference_name': frm.doc.sales_invoice,
						'docstatus': 1,
						'payment_type': 'Receive'
					}
				};
			});
		}
	},
	
	payment_entry: function(frm) {
		if (frm.doc.payment_entry) {
			// Fetch payment entry details
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Payment Entry',
					name: frm.doc.payment_entry
				},
				callback: function(r) {
					if (r.message) {
						const payment_entry = r.message;
						
						// Set transaction details
						frm.set_value('transaction_id', payment_entry.reference_no);
						frm.set_value('gross_amount', payment_entry.paid_amount);
						frm.set_value('bank_account', payment_entry.paid_to);
						
						// Calculate net amount
						calculate_net_amount(frm);
					}
				}
			});
		}
	},
	
	transaction_fee: function(frm) {
		calculate_net_amount(frm);
	},
	
	transaction_fee_vat: function(frm) {
		calculate_net_amount(frm);
	},
	
	gross_amount: function(frm) {
		calculate_net_amount(frm);
	}
});

function calculate_net_amount(frm) {
	const gross_amount = flt(frm.doc.gross_amount);
	const transaction_fee = flt(frm.doc.transaction_fee);
	const transaction_fee_vat = flt(frm.doc.transaction_fee_vat);
	
	const net_amount = gross_amount - transaction_fee - transaction_fee_vat;
	frm.set_value('net_amount', net_amount);
}

function set_account_filters(frm) {
	// Set account filters for all account fields
	const account_fields = [
		'payment_processor_account',
		'hold_account', 
		'loss_account',
		'bank_account',
		'transaction_fee_account'
	];
	
	account_fields.forEach(function(field) {
		frm.set_query(field, function() {
			return {
				filters: {
					'company': frm.doc.company,
					'is_group': 0
				}
			};
		});
	});
}

function fetch_default_accounts(frm) {
	if (!frm.doc.company) return;
	
	// Fetch default accounts in real-time
	const account_mappings = [
		{field: 'payment_processor_account', pattern: 'Payment Processor'},
		{field: 'hold_account', pattern: 'Funds on Hold'},
		{field: 'loss_account', pattern: 'Loss on Payment Processing'},
		{field: 'transaction_fee_account', pattern: 'Transaction Fee'}
	];
	
	account_mappings.forEach(function(mapping) {
		if (!frm.doc[mapping.field]) {
			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Account',
					filters: {
						'company': frm.doc.company,
						'is_group': 0,
						'account_name': ['like', '%' + mapping.pattern + '%']
					},
					fields: ['name'],
					limit: 1
				},
				callback: function(r) {
					if (r.message && r.message.length > 0) {
						frm.set_value(mapping.field, r.message[0].name);
					}
				}
			});
		}
	});
}

// Custom method to validate before submit
frappe.ui.form.on('Funds Hold', 'before_submit', function(frm) {
	// Ensure all required accounts are set
	const required_accounts = ['hold_account', 'transaction_fee_account'];
	let missing_accounts = [];
	
	required_accounts.forEach(function(account) {
		if (!frm.doc[account]) {
			missing_accounts.push(frappe.meta.get_label(frm.doc.doctype, account));
		}
	});
	
	if (missing_accounts.length > 0) {
		frappe.throw(__('Please set the following accounts: {0}', [missing_accounts.join(', ')]));
	}
	
	// Validate amounts
	if (frm.doc.net_amount <= 0) {
		frappe.throw(__('Net Amount must be positive'));
	}
});