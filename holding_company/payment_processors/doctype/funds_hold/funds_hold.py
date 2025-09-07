import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class FundsHold(Document):
	pass
	
	def on_submit(self):
		"""Create journal entry on submit"""
		self.create_journal_entry()
	
	def create_journal_entry(self):
		"""Create journal entry for funds hold transaction"""
		if self.journal_entry:
			return
			
		je_doc = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": self.company,
			"posting_date": self.posting_date or nowdate(),
			"user_remark": f"Funds hold for transaction {self.transaction_id}",
			"accounts": self.get_journal_entry_accounts()
		})
		
		je_doc.insert()
		je_doc.submit()
		
		self.db_set("journal_entry", je_doc.name)
	
	def get_journal_entry_accounts(self):
		"""Get accounts for journal entry"""
		accounts = []
		
		# Debit: Payment Processor Account (or Bank Account)
		debit_account = self.payment_processor_account or self.bank_account
		if debit_account and self.gross_amount:
			accounts.append({
				"account": debit_account,
				"debit_in_account_currency": self.gross_amount,
				"credit_in_account_currency": 0
			})
		
		# Credit: Hold Account (Net Amount)
		if self.hold_account and self.net_amount:
			accounts.append({
				"account": self.hold_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": self.net_amount
			})
		
		# Credit: Transaction Fee Account
		if self.transaction_fee_account and self.transaction_fee:
			accounts.append({
				"account": self.transaction_fee_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": self.transaction_fee
			})
		
		# Credit: Transaction Fee VAT (can be same account or separate)
		if self.transaction_fee_account and self.transaction_fee_vat:
			accounts.append({
				"account": self.transaction_fee_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": self.transaction_fee_vat
			})
		
		return accounts