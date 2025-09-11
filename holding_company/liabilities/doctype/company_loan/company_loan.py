import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class CompanyLoan(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.create_journal_entry()
		self.initialize_loan_tracking()

	def on_cancel(self):
		self.cancel_journal_entry()

	def on_amend(self):
		"""Actions to perform when document is amended"""
		self.journal_entry = None


	def create_journal_entry(self):
		"""Create Journal Entry for loan disbursement"""
		if not self.loan_amount or not self.bank_account or not self.liability_account:
			frappe.throw(_("Loan Amount, Bank Account, and Liability Account are required to create Journal Entry"))

		gl_entry = frappe.new_doc("Journal Entry")
		gl_entry.posting_date = self.posting_date or nowdate()
		gl_entry.company = self.company
		gl_entry.voucher_type = "Bank Entry"
		gl_entry.cheque_no = self.name
		gl_entry.cheque_date = self.posting_date or nowdate()
		gl_entry.user_remark = f"Loan disbursement from {self.lender} - {self.name}"

		# Debit Bank Account (Cash/Asset increase)
		gl_entry.append("accounts", {
			"account": self.bank_account,
			"debit_in_account_currency": flt(self.loan_amount),
			"credit_in_account_currency": 0,
		})

		# Credit Liability Account (Liability increase)
		gl_entry.append("accounts", {
			"account": self.liability_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": flt(self.loan_amount),
		})

		try:
			gl_entry.insert()
			gl_entry.submit()
			
			# Link the journal entry to this loan
			self.db_set("journal_entry", gl_entry.name)
			
			frappe.msgprint("Journal Entry for loan disbursement created successfully.")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not create Journal Entry for Company Loan {self.name}: {e}",
				title="Company Loan Journal Entry Creation Error"
			)
			frappe.throw(f"Error creating Journal Entry: {e}")

	def cancel_journal_entry(self):
		"""Cancel the linked Journal Entry when loan is cancelled"""
		if self.journal_entry:
			try:
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				if je.docstatus == 1:
					je.cancel()
					frappe.msgprint(f"Associated Journal Entry {je.name} has been cancelled.")
				else:
					frappe.msgprint(f"Associated Journal Entry {je.name} was already cancelled.")
				
			except Exception as e:
				frappe.log_error(
					message=f"Could not cancel Journal Entry for Company Loan {self.name}: {e}",
					title="Company Loan Journal Entry Cancellation Error"
				)

	def initialize_loan_tracking(self):
		"""Initialize loan tracking fields"""
		# Initialize tracking fields
		frappe.db.set_value("Company Loan", self.name, {
			"total_repaid": 0,
			"outstanding_balance": self.loan_amount,
			"custom_status": "Unpaid"
		})


