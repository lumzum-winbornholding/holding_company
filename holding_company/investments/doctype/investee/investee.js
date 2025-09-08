frappe.ui.form.on('Investee', {
	setup: function(frm) {
		frm.make_methods = {
			'Contact': function() { 
				frappe.model.open_mapped_doc({
					method: "holding_company.investments.doctype.investee.investee.make_contact",
					frm: frm
				});
			},
			'Address': function() { 
				frappe.model.open_mapped_doc({
					method: "holding_company.investments.doctype.investee.investee.make_address",
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

	investee_primary_address: function(frm) {
		erpnext.utils.get_address_display(frm, "investee_primary_address", "primary_address", false);
	},

	investee_primary_contact: function(frm) {
		erpnext.utils.get_contact_details(frm);
	}
});