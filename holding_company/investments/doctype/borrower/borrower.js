frappe.ui.form.on('Borrower', {
	setup: function(frm) {
		frm.make_methods = {
			'Contact': function() { 
				frappe.model.open_mapped_doc({
					method: "holding_company.investments.doctype.borrower.borrower.make_contact",
					frm: frm
				});
			},
			'Address': function() { 
				frappe.model.open_mapped_doc({
					method: "holding_company.investments.doctype.borrower.borrower.make_address",
					frm: frm
				});
			},
		};
	},

	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			frappe.contacts.render_address_and_contact(frm);
		} else {
			frappe.contacts.clear_address_and_contact(frm);
		}
	},

	borrower_primary_address: function(frm) {
		erpnext.utils.get_address_display(frm, "borrower_primary_address", "primary_address", false);
	},

	borrower_primary_contact: function(frm) {
		erpnext.utils.get_contact_details(frm);
	}
});