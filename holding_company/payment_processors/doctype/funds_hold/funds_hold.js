console.log('Funds Hold JS file loaded');

frappe.ui.form.on('Funds Hold', {
    refresh: function(frm) {
        console.log('Funds Hold form refreshed');
    },
    payment_entry: function(frm) {
        console.log('Payment entry changed:', frm.doc.payment_entry);
        if (frm.doc.payment_entry && frm.doc.company) {
            fetch_mode_of_payment_accounts(frm);
        }
    },
    
    gross_amount: function(frm) {
        calculate_amounts(frm);
    },
    
    transaction_fee: function(frm) {
        calculate_amounts(frm);
    }
});

function fetch_mode_of_payment_accounts(frm) {
    // Fetch the mode of payment from Payment Entry
    frappe.db.get_value('Payment Entry', frm.doc.payment_entry, 'mode_of_payment')
        .then(r => {
            if (r.message && r.message.mode_of_payment) {
                const mode_of_payment = r.message.mode_of_payment;
                
                // Fetch Mode of Payment document with its accounts child table
                frappe.call({
                    method: 'frappe.client.get',
                    args: {
                        doctype: 'Mode of Payment',
                        name: mode_of_payment
                    },
                    callback: function(response) {
                        if (response.message) {
                            const mode_of_payment_doc = response.message;
                            const accounts = mode_of_payment_doc.accounts || [];
                            
                            // Find account entry matching the company
                            const company_account = accounts.find(account => 
                                account.company === frm.doc.company
                            );
                            
                            if (company_account) {
                                // Map the fields from Mode of Payment Account to Funds Hold
                                frm.set_value('payment_processor_account', company_account.default_account);
                                frm.set_value('hold_account', company_account.custom_hold_account);
                                frm.set_value('loss_account', company_account.custom_losses_account);
                                frm.set_value('bank_account', company_account.custom_bank_account);
                                frm.set_value('transaction_fee_account', company_account.custom_transaction_fees_account);
                            }
                        }
                    }
                });
            }
        });
}

function calculate_amounts(frm) {
    if (frm.doc.gross_amount && frm.doc.transaction_fee) {
        // Calculate transaction fee VAT (7%)
        const transaction_fee_vat = flt(frm.doc.transaction_fee * 0.07, 2);
        frm.set_value('transaction_fee_vat', transaction_fee_vat);
        
        // Calculate net amount
        const gross_amount = flt(frm.doc.gross_amount, 2);
        const transaction_fee = flt(frm.doc.transaction_fee, 2);
        const net_amount = gross_amount - transaction_fee - transaction_fee_vat;
        
        frm.set_value('net_amount', flt(net_amount, 2));
    }
}