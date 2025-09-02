frappe.ui.form.on("Company", {
    refresh: function(frm) {
        // Add WIN BORN template option to chart of accounts
        if (frm.fields_dict.chart_of_accounts) {
            let options = frm.get_field("chart_of_accounts").df.options.split("\n");
            if (!options.includes("WIN BORN HOLDING Template")) {
                options.push("WIN BORN HOLDING Template");
                frm.set_df_property("chart_of_accounts", "options", options.join("\n"));
            }
        }
    }
});