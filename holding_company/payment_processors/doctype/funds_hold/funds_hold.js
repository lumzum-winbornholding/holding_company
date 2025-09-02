// Basic Funds Hold JavaScript

frappe.ui.form.on('Funds Hold', {
    transaction_fee: function(frm) {
        // Calculate VAT when transaction fee changes
        if (frm.doc.transaction_fee) {
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
        // Recalculate when gross amount changes
        if (frm.doc.gross_amount && frm.doc.transaction_fee && frm.doc.transaction_fee_vat) {
            let net = frm.doc.gross_amount - frm.doc.transaction_fee - frm.doc.transaction_fee_vat;
            frm.set_value('net_amount', net);
        }
    }
});