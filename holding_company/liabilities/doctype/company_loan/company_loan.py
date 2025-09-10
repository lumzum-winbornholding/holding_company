import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class CompanyLoan(Document):
	def validate(self):
		self.calculate_outstanding_balance()
		self.update_loan_status()

	def on_submit(self):
		self.create_journal_entry()
		self.calculate_outstanding_balance()
		self.update_loan_status()

	def on_cancel(self):
		self.cancel_journal_entry()

	def calculate_outstanding_balance(self):
		"""Calculate outstanding balance and update tracking fields"""
		if self.loan_amount:
			total_repaid = flt(self.total_repaid) if self.total_repaid else 0
			self.outstanding_balance = flt(self.loan_amount) - total_repaid

	def update_loan_status(self):
		"""Update loan status based on repayment progress"""
		total_repaid = flt(self.total_repaid) if self.total_repaid else 0
		
		if total_repaid == 0:
			self.custom_status = "Unpaid"
		elif total_repaid > 0 and flt(self.outstanding_balance) > 0:
			self.custom_status = "Partially Repaid"
		elif flt(self.outstanding_balance) <= 0:
			self.custom_status = "Repaid"

	def create_journal_entry(self):
		"""Create Journal Entry for loan disbursement"""
		if not self.loan_amount or not self.bank_account or not self.liability_account:
			frappe.throw(_("Loan Amount, Bank Account, and Liability Account are required to create Journal Entry"))

		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = self.date or nowdate()
		je.company = self.company
		je.remark = _("Loan disbursement from {0} - {1}").format(self.lender, self.name)

		# Debit Bank Account (Cash/Asset increase)
		je.append("accounts", {
			"account": self.bank_account,
			"debit_in_account_currency": flt(self.loan_amount),
			"credit_in_account_currency": 0,
		})

		# Credit Liability Account (Liability increase)
		je.append("accounts", {
			"account": self.liability_account,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": flt(self.loan_amount),
		})

		try:
			je.insert()
			je.submit()
			
			# Link the journal entry to this loan
			self.db_set("journal_entry", je.name)
			
			frappe.msgprint(_("Journal Entry {0} created successfully").format(je.name))
			
		except Exception as e:
			frappe.throw(_("Error creating Journal Entry: {0}").format(str(e)))

	def cancel_journal_entry(self):
		"""Cancel the linked Journal Entry when loan is cancelled"""
		if self.journal_entry:
			try:
				je = frappe.get_doc("Journal Entry", self.journal_entry)
				if je.docstatus == 1:
					je.cancel()
				
				frappe.msgprint(_("Journal Entry {0} cancelled successfully").format(self.journal_entry))
				
			except Exception as e:
				frappe.msgprint(_("Error cancelling Journal Entry: {0}").format(str(e)))


@frappe.whitelist()
def update_loan_repayments(loan_name):
	"""Update loan repayment tracking when repayments are made"""
	loan = frappe.get_doc("Company Loan", loan_name)
	
	# Calculate total repaid from all Company Loan Repayment records
	total_repaid = frappe.db.sql("""
		SELECT SUM(repayment_amount) as total
		FROM `tabCompany Loan Repayment`
		WHERE company_loan = %s AND docstatus = 1
	""", (loan_name,), as_dict=True)
	
	total_repaid_amount = flt(total_repaid[0].total) if total_repaid and total_repaid[0].total else 0
	
	# Update loan tracking fields
	loan.db_set("total_repaid", total_repaid_amount)
	loan.calculate_outstanding_balance()
	loan.update_loan_status()
	
	# Save the updated status and outstanding balance
	loan.db_set("outstanding_balance", loan.outstanding_balance)
	loan.db_set("custom_status", loan.custom_status)
	
	return {
		"total_repaid": total_repaid_amount,
		"outstanding_balance": loan.outstanding_balance,
		"custom_status": loan.custom_status
	}