import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class CompanyLoanRepayment(Document):
	def validate(self):
		self.calculate_net_amount()

	def on_submit(self):
		self.create_journal_entry()
		self.update_parent_loan()

	def on_cancel(self):
		self.cancel_journal_entry()
		self.update_parent_loan()

	def on_amend(self):
		"""Actions to perform when document is amended"""
		self.journal_entry = None

	def calculate_net_amount(self):
		"""Calculate net amount (principal + interest)"""
		if self.repayment_amount and self.repayment_interest:
			self.net_amount = flt(self.repayment_amount) + flt(self.repayment_interest)

	def create_journal_entry(self):
		"""Create Journal Entry for loan repayment"""
		if self.journal_entry:
			frappe.throw(_("Journal Entry already exists"))

		if not self.repayment_amount or not self.bank_account or not self.liability_account:
			frappe.throw(_("Repayment Amount, Bank Account, and Liability Account are required to create Journal Entry"))

		try:
			# Get Company Loan document for reference
			loan = frappe.get_doc("Company Loan", self.company_loan) if self.company_loan else None
			
			gl_entry = frappe.new_doc("Journal Entry")
			gl_entry.posting_date = self.date or nowdate()
			gl_entry.company = self.company
			gl_entry.voucher_type = "Bank Entry"
			gl_entry.cheque_no = self.name
			gl_entry.cheque_date = self.date or nowdate()
			gl_entry.user_remark = f"Repayment for Company Loan {loan.name}" if loan else f"Repayment for Company Loan - {self.name}"

			# Credit net_amount to bank_account (Cash/Asset decrease)
			net_amount = flt(self.net_amount) or (flt(self.repayment_amount) + flt(self.repayment_interest or 0))
			gl_entry.append("accounts", {
				"account": self.bank_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": net_amount,
			})

			# Debit repayment_amount to liability_account (Liability decrease)
			gl_entry.append("accounts", {
				"account": self.liability_account,
				"debit_in_account_currency": flt(self.repayment_amount),
				"credit_in_account_currency": 0,
			})

			# Debit repayment_interest to interest_expense_account (if applicable)
			if self.repayment_interest and flt(self.repayment_interest) > 0:
				gl_entry.append("accounts", {
					"account": self.interest_expense_account,
					"debit_in_account_currency": flt(self.repayment_interest),
					"credit_in_account_currency": 0,
				})

			gl_entry.insert()
			gl_entry.submit()
			
			# Link the journal entry to this repayment
			self.db_set("journal_entry", gl_entry.name)
			
			frappe.msgprint(_("Journal Entry {0} created successfully").format(gl_entry.name))
			
		except Exception as e:
			frappe.msgprint(_("Error creating Journal Entry: {0}").format(str(e)))
			frappe.log_error(
				message=f"Error creating Journal Entry for Company Loan Repayment {self.name}: {e}",
				title="Company Loan Repayment Journal Entry Error"
			)

	def cancel_journal_entry(self):
		"""Cancel the linked Journal Entry when repayment is cancelled"""
		if self.journal_entry:
			try:
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				if je.docstatus == 1:
					je.cancel()
				
				frappe.msgprint(_("Journal Entry {0} cancelled successfully").format(self.journal_entry))
				
			except Exception as e:
				frappe.msgprint(_("Error cancelling Journal Entry: {0}").format(str(e)))

	def update_parent_loan(self):
		"""Update the parent Company Loan tracking fields"""
		if self.company_loan:
			try:
				# Call the update function from Company Loan
				from holding_company.liabilities.doctype.company_loan.company_loan import update_loan_repayments
				result = update_loan_repayments(self.company_loan)
				
				if result:
					frappe.msgprint(_("Company Loan tracking updated - Outstanding Balance: {0}").format(
						frappe.utils.fmt_money(result.get('outstanding_balance'), currency=frappe.defaults.get_global_default('currency'))
					))
					
			except Exception as e:
				frappe.log_error(
					message=f"Could not update loan repayments for Company Loan {self.company_loan}: {e}",
					title="Company Loan Repayment Update Error"
				)
				frappe.msgprint(_("Error updating Company Loan tracking: {0}").format(str(e)))