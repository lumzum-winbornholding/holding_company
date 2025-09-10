import frappe
from frappe.model.document import Document
from frappe.utils import flt


class InvestmentReturn(Document):
	def on_submit(self):
		"""Create journal entry and update Investment ROI when Investment Return is submitted"""
		if self.investment and self.dividend_amount:
			self.create_journal_entry()
			self.update_investment_roi()
	
	def on_cancel(self):
		"""Cancel journal entry and reverse ROI calculation when Investment Return is cancelled"""
		if self.investment and self.dividend_amount:
			self.cancel_journal_entry()
			self.update_investment_roi(reverse=True)
	
	def on_amend(self):
		"""Clear journal entry field when document is amended"""
		self.journal_entry = None
	
	def create_journal_entry(self):
		"""Create journal entry for dividend transaction"""
		if self.journal_entry:
			frappe.throw("Journal Entry already exists")
		
		try:
			# Get investee full name
			investee_doc = frappe.get_doc("Investee", self.investee)
			investee_full_name = investee_doc.investee_name or self.investee
			
			# Create a new Journal Entry document
			je = frappe.new_doc("Journal Entry")
			
			# Populate the header fields
			je.posting_date = self.date
			je.company = self.company
			je.voucher_type = "Bank Entry"
			je.cheque_no = self.name
			je.cheque_date = self.date
			je.user_remark = f"Dividend received from {investee_full_name}"
			
			# Add the accounting lines
			# Line 1: Debit the Bank Account (cash received)
			je.append("accounts", {
				"account": self.bank_account,
				"debit_in_account_currency": self.dividend_amount
			})
			
			# Line 2: Credit the Dividend Income Account (income recognition)
			je.append("accounts", {
				"account": self.dividend_income_account,
				"credit_in_account_currency": self.dividend_amount,
				"reference_type": "Investment",
				"reference_name": self.investment
			})
			
			# Save and submit the Journal Entry
			je.save()
			je.submit()
			
			# Link the JE to this document
			self.db_set('journal_entry', je.name)
			
			frappe.msgprint("Dividend journal entry created successfully.")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not create Journal Entry for Investment Return {self.name}: {e}",
				title="Investment Return Journal Entry Creation Error"
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
					message=f"Could not cancel Journal Entry for Investment Return {self.name}: {e}",
					title="Investment Return Journal Entry Cancellation Error"
				)
	
	def update_investment_roi(self, reverse=False):
		"""Update the Investment's ROI and dividend_paid fields"""
		try:
			# Get the Investment document
			investment_doc = frappe.get_doc("Investment", self.investment)
			
			# Calculate the dividend amount (positive for submit, negative for cancel)
			dividend_amount = flt(self.dividend_amount)
			if reverse:
				dividend_amount = -dividend_amount
			
			# Update dividend_paid (total dividends received)
			current_dividend_paid = flt(investment_doc.dividend_paid)
			new_dividend_paid = current_dividend_paid + dividend_amount
			
			# Update ROI (starts negative, becomes positive with dividends)
			current_roi = flt(investment_doc.roi)
			new_roi = current_roi + dividend_amount
			
			# Determine investment status based on ROI
			if new_roi >= 0:
				investment_status = "Recovered"
			else:
				investment_status = "Unrecovered"
			
			# Update the Investment document
			frappe.db.set_value("Investment", self.investment, {
				"dividend_paid": new_dividend_paid,
				"roi": new_roi,
				"custom_status": investment_status
			})
			
			# Show confirmation message
			action = "updated" if not reverse else "reversed"
			frappe.msgprint(f"Investment tracking {action}. New ROI: {new_roi}, Status: {investment_status}")
			
		except Exception as e:
			frappe.log_error(
				message=f"Could not update Investment ROI for Investment Return {self.name}: {e}",
				title="Investment ROI Update Error"
			)
			if not reverse:  # Only throw error on submit, not cancel
				frappe.throw(f"Error updating Investment ROI: {e}")