import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Investment(Document):
	def on_submit(self):
		"""Initialize ROI and create journal entry when Investment is submitted"""
		self.create_journal_entry()
		self.initialize_roi()
	
	def on_cancel(self):
		"""Cancel related journal entry when Investment is cancelled"""
		self.cancel_journal_entry()
	
	def on_amend(self):
		"""Clear journal entry field when document is amended"""
		self.journal_entry = None
	
	def create_journal_entry(self):
		"""Create journal entry for investment transaction"""
		if self.journal_entry:
			frappe.throw("Journal Entry already exists")
		
		try:
			# Get investee full name
			investee_doc = frappe.get_doc("Investee", self.investee)
			investee_full_name = investee_doc.investee_name or self.investee
			
			# Create a new Journal Entry document
			je = frappe.new_doc("Journal Entry")
			
			# Populate the header fields
			je.posting_date = self.posting_date
			je.company = self.company
			je.voucher_type = "Bank Entry"
			je.cheque_no = self.name
			je.cheque_date = self.posting_date
			je.user_remark = f"Investment in {investee_full_name}"
			
			# Add the accounting lines
			# Line 1: Debit the Investment Account
			je.append("accounts", {
				"account": self.investment_account,
				"debit_in_account_currency": self.investment_amount
			})
			
			# Line 2: Credit the Bank Account
			je.append("accounts", {
				"account": self.bank_account,
				"credit_in_account_currency": self.investment_amount
			})
			
			# Save and submit the Journal Entry
			je.save()
			je.submit()
			
			# Link the JE to this document
			self.db_set('journal_entry', je.name)
			
			frappe.msgprint("Journal Entry created and ROI balance initialized.")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not create Journal Entry for Investment {self.name}: {e}",
				title="Investment Journal Entry Creation Error"
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
					message=f"Could not cancel Journal Entry for Investment {self.name}: {e}",
					title="Investment Journal Entry Cancellation Error"
				)
	
	def initialize_roi(self):
		"""Set initial ROI to negative investment amount and status to Unrecovered"""
		if self.investment_amount:
			initial_roi = -flt(self.investment_amount)
			
			# Update ROI and status
			frappe.db.set_value("Investment", self.name, {
				"roi": initial_roi,
				"dividend_paid": 0,
				"custom_status": "Unrecovered"
			})