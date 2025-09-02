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

// Funds Hold functionality (since doctype JS isn't loading)
frappe.ui.form.on('Funds Hold', {
    transaction_fee: function(frm) {
        console.log('Transaction fee changed in global JS:', frm.doc.transaction_fee);
        if (frm.doc.transaction_fee) {
            // Calculate VAT (7%)
            let vat = frm.doc.transaction_fee * 0.07;
            frm.set_value('transaction_fee_vat', vat);
            
            // Calculate net amount if gross amount exists
            if (frm.doc.gross_amount) {
                let net = frm.doc.gross_amount - frm.doc.transaction_fee - vat;
                frm.set_value('net_amount', net);
            }
        }
    },

    gross_amount: function(frm) {
        console.log('Gross amount changed in global JS:', frm.doc.gross_amount);
        if (frm.doc.gross_amount && frm.doc.transaction_fee && frm.doc.transaction_fee_vat) {
            let net = frm.doc.gross_amount - frm.doc.transaction_fee - frm.doc.transaction_fee_vat;
            frm.set_value('net_amount', net);
        }
    },

    refresh: function(frm) {
        console.log('Funds Hold form loaded via global JS');
    }
});