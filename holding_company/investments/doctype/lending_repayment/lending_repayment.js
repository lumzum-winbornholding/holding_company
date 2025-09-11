frappe.ui.form.on('Lending Repayment', {
	refresh: function(frm) {
		// Clear journal_entry field (it will be auto-populated when created from Lending)
		if (frm.doc.__islocal) {
			frm.set_value('journal_entry', '');
		}
		
		// Only disable save if there's no lending linked
		if (frm.doc.__islocal && !frm.doc.lending) {
			frm.disable_save();
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Lending Repayment records can only be created from Lending. Please use the "Create Repayment" button in Lending form.'),
				indicator: 'red'
			});
		}
	},
	
	lending: function(frm) {
		if (frm.doc.lending) {
			fetch_lending_data(frm);
		}
	},
	
	repayment_amount: function(frm) {
		calculate_net_amount(frm);
	},
	
	repayment_interest: function(frm) {
		calculate_net_amount(frm);
	}
});

function calculate_net_amount(frm) {
	const repayment_amount = flt(frm.doc.repayment_amount);
	const repayment_interest = flt(frm.doc.repayment_interest);
	
	const net_amount = repayment_amount + repayment_interest;
	frm.set_value('net_amount', net_amount);
}