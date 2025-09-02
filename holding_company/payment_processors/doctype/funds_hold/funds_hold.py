import frappe
from frappe.model.document import Document

class FundsHold(Document):
    def validate(self):
        """Calculate amounts automatically when document is validated"""
        if self.transaction_fee:
            # Calculate VAT (7%)
            self.transaction_fee_vat = self.transaction_fee * 0.07
            
            # Calculate net amount if gross amount exists
            if self.gross_amount:
                self.net_amount = self.gross_amount - self.transaction_fee - (self.transaction_fee_vat or 0)