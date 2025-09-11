import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Lending(Document):
	def on_submit(self):
		"""Create journal entry and initialize loan tracking when Lending is submitted"""
		self.create_journal_entry()
		self.initialize_loan_tracking()
	
	def on_cancel(self):
		"""Cancel related journal entry when Lending is cancelled"""
		self.cancel_journal_entry()
	
	def on_amend(self):
		"""Clear journal entry field when document is amended"""
		self.journal_entry = None
	
	def create_journal_entry(self):
		"""Create journal entry for loan disbursement"""
		if self.journal_entry:
			frappe.throw("Journal Entry already exists")
		
		try:
			# Get borrower full name
			borrower_doc = frappe.get_doc("Borrower", self.borrower)
			borrower_full_name = borrower_doc.borrower_name or self.borrower
			
			# Create a new Journal Entry document
			gl_entry = frappe.new_doc("Journal Entry")
			
			# Populate the header fields
			gl_entry.posting_date = self.posting_date
			gl_entry.company = self.company
			gl_entry.voucher_type = "Bank Entry"
			gl_entry.cheque_no = self.name
			gl_entry.cheque_date = self.posting_date
			gl_entry.user_remark = f"Loan disbursement for {self.name} to {borrower_full_name}"
			
			# Add the accounting lines
			# Line 1: Debit the Loan Account (Asset - Amount lent out)
			gl_entry.append("accounts", {
				"account": self.loan_account,
				"debit_in_account_currency": self.loan_amount,
				"party_type": "Borrower",
				"party": self.borrower
			})
			
			# Line 2: Credit the Bank Account (Cash paid out)
			gl_entry.append("accounts", {
				"account": self.bank_account,
				"credit_in_account_currency": self.loan_amount
			})
			
			# Save and submit the Journal Entry
			gl_entry.save()
			gl_entry.submit()
			
			# Link the JE to this document
			self.db_set('journal_entry', gl_entry.name)
			
			frappe.msgprint("Journal Entry for loan disbursement created successfully.")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not create Journal Entry for Lending {self.name}: {e}",
				title="Lending Journal Entry Creation Error"
			)
			frappe.throw(f"Error creating Journal Entry: {e}")
	
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
					message=f"Could not cancel Journal Entry for Lending {self.name}: {e}",
					title="Lending Journal Entry Cancellation Error"
				)
	
	def initialize_loan_tracking(self):
		"""Initialize loan tracking fields"""
		# Initialize tracking fields
		frappe.db.set_value("Lending", self.name, {
			"total_repaid": 0,
			"outstanding_balance": self.loan_amount,
			"custom_status": "Unpaid"
		})