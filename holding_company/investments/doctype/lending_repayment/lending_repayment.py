import frappe
from frappe.model.document import Document
from frappe.utils import flt


class LendingRepayment(Document):
	def on_submit(self):
		"""Create journal entry and update lending tracking when Lending Repayment is submitted"""
		if self.lending and self.repayment_amount:
			self.create_journal_entry()
			self.update_lending_tracking()
	
	def on_cancel(self):
		"""Cancel journal entry and reverse lending tracking when Lending Repayment is cancelled"""
		if self.lending and self.repayment_amount:
			self.cancel_journal_entry()
			self.update_lending_tracking(reverse=True)
	
	def on_amend(self):
		"""Clear journal entry field when document is amended"""
		self.journal_entry = None
	
	def create_journal_entry(self):
		"""Create journal entry for loan repayment"""
		if self.journal_entry:
			frappe.throw("Journal Entry already exists")
		
		try:
			# Get borrower full name and lending details
			borrower_doc = frappe.get_doc("Borrower", self.borrower)
			borrower_full_name = borrower_doc.borrower_name or self.borrower
			lending_doc = frappe.get_doc("Lending", self.lending)
			
			# Create a new Journal Entry document
			gl_entry = frappe.new_doc("Journal Entry")
			
			# Populate the header fields
			gl_entry.posting_date = self.posting_date
			gl_entry.company = self.company
			gl_entry.voucher_type = "Bank Entry"
			gl_entry.cheque_no = self.name
			gl_entry.cheque_date = self.posting_date
			gl_entry.user_remark = f"Repayment for Lending {lending_doc.name}"
			
			# Add the accounting lines
			# Line 1: Debit the Bank Account (cash received)
			gl_entry.append("accounts", {
				"account": self.bank_account,
				"debit_in_account_currency": self.net_amount,
			})
			
			# Line 2: Credit the Loan Account (principal repayment)
			if self.repayment_amount:
				gl_entry.append("accounts", {
					"account": self.loan_account,
					"credit_in_account_currency": self.repayment_amount,
					"party_type": "Borrower",
					"party": self.borrower
				})
			
			# Line 3: Credit the Interest Income Account (interest earned)
			if self.repayment_interest:
				gl_entry.append("accounts", {
					"account": self.interest_income_account,
					"credit_in_account_currency": self.repayment_interest
				})
			
			# Save and submit the Journal Entry
			gl_entry.save()
			gl_entry.submit()
			
			# Link the JE to this document
			self.db_set('journal_entry', gl_entry.name)
			
			frappe.msgprint("Journal Entry for loan repayment created successfully.")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not create Journal Entry for Lending Repayment {self.name}: {e}",
				title="Lending Repayment Journal Entry Creation Error"
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
					message=f"Could not cancel Journal Entry for Lending Repayment {self.name}: {e}",
					title="Lending Repayment Journal Entry Cancellation Error"
				)
	
	def update_lending_tracking(self, reverse=False):
		"""Update the Lending's total_repaid, outstanding_balance and status directly"""
		try:
			# Get the Lending document
			lending_doc = frappe.get_doc("Lending", self.lending)
			loan_amount = flt(lending_doc.loan_amount)
			
			# Calculate the repayment amount (positive for submit, negative for cancel)
			repayment_amount = flt(self.repayment_amount)
			if reverse:
				repayment_amount = -repayment_amount
			
			# Update total_repaid (total repayments received)
			current_total_repaid = flt(lending_doc.total_repaid)
			new_total_repaid = current_total_repaid + repayment_amount
			
			# Ensure total_repaid doesn't go negative on cancellation
			if new_total_repaid < 0:
				new_total_repaid = 0
			
			# Calculate outstanding_balance = Loan Amount - Total Repaid
			new_outstanding_balance = loan_amount - new_total_repaid
			
			# Ensure outstanding balance doesn't go negative
			if new_outstanding_balance < 0:
				new_outstanding_balance = 0
			
			# Determine loan status based on repayment
			if new_total_repaid == 0:
				loan_status = "Unpaid"
			elif new_outstanding_balance == 0 or new_total_repaid >= loan_amount:
				loan_status = "Repaid"
			else:
				loan_status = "Partially Repaid"
			
			# Update the Lending document
			frappe.db.set_value("Lending", self.lending, {
				"total_repaid": new_total_repaid,
				"outstanding_balance": new_outstanding_balance,
				"custom_status": loan_status
			})
			
			# Show confirmation message
			action = "updated" if not reverse else "reversed"
			frappe.msgprint(f"Lending tracking {action}. Total Repaid: {new_total_repaid}, Outstanding: {new_outstanding_balance}, Status: {loan_status}")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not update Lending tracking for Lending Repayment {self.name}: {e}",
				title="Lending Tracking Update Error"
			)
			if not reverse:  # Only throw error on submit, not cancel
				frappe.throw(f"Error updating Lending tracking: {e}")