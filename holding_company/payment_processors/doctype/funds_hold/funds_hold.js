frappe.ui.form.on('Funds Hold', {
    payment_entry: function(frm) {
        console.log('Payment Entry changed:', frm.doc.payment_entry);
        if (frm.doc.payment_entry && frm.doc.company) {
            console.log('Fetching Payment Entry details...');
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Payment Entry',
                    name: frm.doc.payment_entry
                },
                callback: function(r) {
                    console.log('Payment Entry response:', r);
                    if (r.message && r.message.mode_of_payment) {
                        console.log('Mode of Payment found:', r.message.mode_of_payment);
                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: {
                                doctype: 'Mode of Payment Account',
                                filters: {
                                    parent: r.message.mode_of_payment,
                                    company: frm.doc.company
                                },
                                fields: ['default_account', 'custom_hold_account', 'custom_losses_account', 'custom_bank_account', 'custom_transaction_fees_account']
                            },
                            callback: function(account_r) {
                                console.log('Mode of Payment Account response:', account_r);
                                if (account_r.message && account_r.message.length > 0) {
                                    let account = account_r.message[0];
                                    console.log('Account data:', account);
                                    frm.set_value('payment_processor_account', account.default_account);
                                    frm.set_value('hold_account', account.custom_hold_account);
                                    frm.set_value('loss_account', account.custom_losses_account);
                                    frm.set_value('bank_account', account.custom_bank_account);
                                    frm.set_value('transaction_fee_account', account.custom_transaction_fees_account);
                                } else {
                                    console.log('No Mode of Payment Account found or empty response');
                                }
                            }
                        });
                    } else {
                        console.log('No mode_of_payment found in Payment Entry');
                    }
                }
            });
        } else {
            console.log('Missing payment_entry or company');
        }
    },

    transaction_fee: function(frm) {
        if (frm.doc.transaction_fee) {
            let vat = frm.doc.transaction_fee * 0.07;
            frm.set_value('transaction_fee_vat', vat);
            
            if (frm.doc.gross_amount) {
                let net = frm.doc.gross_amount - frm.doc.transaction_fee - vat;
                frm.set_value('net_amount', net);
            }
        }
    },

    gross_amount: function(frm) {
        if (frm.doc.gross_amount && frm.doc.transaction_fee && frm.doc.transaction_fee_vat) {
            let net = frm.doc.gross_amount - frm.doc.transaction_fee - frm.doc.transaction_fee_vat;
            frm.set_value('net_amount', net);
        }
    }
});