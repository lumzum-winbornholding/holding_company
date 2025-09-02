// Global override for chart of accounts functionality

$(document).ready(function() {
    // Override the global erpnext.company.set_chart_of_accounts_options function
    if (typeof erpnext !== 'undefined' && erpnext.company && erpnext.company.set_chart_of_accounts_options) {
        const original_set_chart_options = erpnext.company.set_chart_of_accounts_options;
        
        erpnext.company.set_chart_of_accounts_options = function(doc) {
            var selected_value = doc.chart_of_accounts;
            if (doc.country) {
                return frappe.call({
                    method: "holding_company.overrides.get_charts_for_country",
                    args: {
                        country: doc.country,
                        with_standard: true,
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            set_field_options("chart_of_accounts", [""].concat(r.message).join("\n"));
                            if (in_list(r.message, selected_value))
                                cur_frm.set_value("chart_of_accounts", selected_value);
                        }
                    },
                });
            }
        };
    }
});