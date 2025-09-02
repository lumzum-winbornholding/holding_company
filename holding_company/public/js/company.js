// Custom Company form enhancements for Holding Company Template

frappe.ui.form.on("Company", {
    refresh: function(frm) {
        // Ensure chart options are refreshed when form loads
        if (frm.doc.country && !frm.doc.chart_of_accounts) {
            erpnext.company.set_chart_of_accounts_options(frm.doc);
        }
    }
});