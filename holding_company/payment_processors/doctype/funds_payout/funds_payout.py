import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FundsPayout(Document):
	def on_submit(self):
		"""Actions to perform when document is submitted"""
		self.create_journal_entry()
	
	def on_cancel(self):
		"""Actions to perform when document is cancelled"""
		self.cancel_journal_entry()
	
	def on_amend(self):
		"""Actions to perform when document is amended"""
		self.journal_entry = None
	
	def create_journal_entry(self):
		"""Create journal entry for funds payout transaction"""
		if self.journal_entry:
			frappe.throw("Journal Entry already exists")
		
		# Create a new Journal Entry document
		je = frappe.new_doc("Journal Entry")
		
		# Populate the header fields
		je.posting_date = self.posting_date
		je.company = self.company
		je.voucher_type = "Journal Entry"
		je.cheque_no = self.name
		je.cheque_date = self.posting_date
		je.user_remark = f"Funds payout for original Payment Entry: {self.payment_entry}"
		
		# Get company abbreviation for VAT account
		company_abbr = frappe.db.get_value("Company", self.company, "abbr")
		vat_account = f"VAT (Assets) - {company_abbr}"
		
		# Add the accounting lines based on creation method
		if self.funds_hold:
			# Created from Funds Hold: Credit gross to hold_account
			je.append("accounts", {
				"account": self.hold_account,
				"credit_in_account_currency": self.gross_amount,
				"reference_type": "Payment Entry",
				"reference_name": self.payment_entry
			})
		else:
			# Manually created: Credit gross to payment_processor_account
			je.append("accounts", {
				"account": self.payment_processor_account,
				"credit_in_account_currency": self.gross_amount,
				"reference_type": "Payment Entry",
				"reference_name": self.payment_entry
			})
		
		# Debit net amount to bank_account
		je.append("accounts", {
			"account": self.bank_account,
			"debit_in_account_currency": self.net_amount
		})
		
		# Debit transaction fee to transaction_fee_account
		if self.transaction_fee:
			je.append("accounts", {
				"account": self.transaction_fee_account,
				"debit_in_account_currency": self.transaction_fee
			})
		
		# Debit VAT to VAT (Assets) account
		if self.transaction_fee_vat:
			je.append("accounts", {
				"account": vat_account,
				"debit_in_account_currency": self.transaction_fee_vat
			})
		
		# Save and submit the Journal Entry
		je.save()
		je.submit()
		
		# Link the JE to this document for cancellation
		self.db_set('journal_entry', je.name)
		
		# Show a confirmation message
		frappe.msgprint(f"Journal Entry {je.name} created successfully.")
	
	def cancel_journal_entry(self):
		"""Cancel related journal entry"""
		if self.journal_entry:
			try:
				# Get the full Journal Entry document
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				
				# Check if it's not already cancelled
				if je.docstatus == 1:
					je.cancel()
					frappe.msgprint(f"Associated Journal Entry {je.name} has been cancelled.")
				else:
					frappe.msgprint(f"Associated Journal Entry {je.name} was already cancelled.")
					
			except Exception as e:
				frappe.log_error(
					message=f"Could not cancel Journal Entry for Funds Payout document {self.name}: {e}",
					title="Funds Payout Cancellation Script Error"
				)