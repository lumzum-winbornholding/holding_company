import frappe
from frappe.model.document import Document
from frappe.utils import flt


class FundsHold(Document):
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
		"""Create journal entry for funds hold transaction"""
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
		je.user_remark = f"Funds held for original Payment Entry: {self.payment_entry}"
		
		# Add the accounting lines
		# Line 1: Debit the "Hold" account
		je.append("accounts", {
			"account": self.hold_account,
			"debit_in_account_currency": self.gross_amount
		})
		
		# Line 2: Credit the payment processor account
		je.append("accounts", {
			"account": self.payment_processor_account,
			"credit_in_account_currency": self.gross_amount,
			"reference_type": "Payment Entry",
			"reference_name": self.payment_entry
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
					message=f"Could not cancel Journal Entry for Funds Hold document {self.name}: {e}",
					title="Funds Hold Cancellation Script Error"
				)