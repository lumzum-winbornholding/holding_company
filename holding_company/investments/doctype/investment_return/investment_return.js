frappe.ui.form.on('Investment Return', {
	refresh: function(frm) {
		// Disable creation of new records manually
		frm.disable_save();
		
		// Clear journal_entry field (it will be auto-populated when created from Investment)
		if (frm.doc.__islocal) {
			frm.set_value('journal_entry', '');
		}
		
		if (frm.doc.__islocal && !frm.doc.investment) {
			frappe.msgprint({
				title: __('Manual Creation Not Allowed'),
				message: __('Investment Return records can only be created from Investment DocType. Please use the "Create Investment Return" button in Investment form.'),
				indicator: 'red'
			});
		}
	}
});