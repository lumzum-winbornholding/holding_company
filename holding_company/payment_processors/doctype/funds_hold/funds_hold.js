frappe.ui.form.on('Funds Hold', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
			frm.set_value('journal_entry', '');
		}
	},
	
	payment_entry: function(frm) {
		if (frm.doc.payment_entry && frm.doc.company) {
			fetch_mode_of_payment_accounts(frm);
		}
	},
	
	transaction_fee: function(frm) {
		if (frm.doc.transaction_fee) {
			const transaction_fee = flt(frm.doc.transaction_fee);
			const transaction_fee_vat = transaction_fee * 0.07;
			frm.set_value('transaction_fee_vat', transaction_fee_vat);
		}
		calculate_net_amount(frm);
	},
	
	gross_amount: function(frm) {
		calculate_net_amount(frm);
	},
	
	transaction_fee_vat: function(frm) {
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

function fetch_mode_of_payment_accounts(frm) {
	// First, get the Payment Entry to find the Mode of Payment
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Payment Entry',
			name: frm.doc.payment_entry
		},
		callback: function(r) {
			if (r.message && r.message.mode_of_payment) {
				const mode_of_payment = r.message.mode_of_payment;
				
				// Now get the Mode of Payment document with its child table
				frappe.call({
					method: 'frappe.client.get',
					args: {
						doctype: 'Mode of Payment',
						name: mode_of_payment
					},
					callback: function(mop_r) {
						if (mop_r.message && mop_r.message.accounts) {
							// Find the account row that matches the company
							const company_account = mop_r.message.accounts.find(
								account => account.company === frm.doc.company
							);
							
							if (company_account) {
								// Map the fields from Mode of Payment Account to Funds Hold
								const field_mappings = {
									'default_account': 'payment_processor_account',
									'custom_hold_account': 'hold_account',
									'custom_transaction_fees_account': 'transaction_fee_account',
									'custom_bank_account': 'bank_account',
									'custom_losses_account': 'loss_account'
								};
								
								// Set the values for each mapped field
								Object.keys(field_mappings).forEach(function(source_field) {
									const target_field = field_mappings[source_field];
									if (company_account[source_field]) {
										frm.set_value(target_field, company_account[source_field]);
									}
								});
								
								frappe.show_alert(__('Account fields updated from Mode of Payment'), 3);
							} else {
								frappe.msgprint(__('No Mode of Payment Account found for company: {0}', [frm.doc.company]));
							}
						}
					}
				});
			}
		}
	});
}