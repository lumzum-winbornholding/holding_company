import frappe
from frappe.model.document import Document


class FundsHold(Document):
	def on_submit(self):
		"""Actions to perform when document is submitted"""
		# Create journal entry
		pass
	
	def on_cancel(self):
		"""Actions to perform when document is cancelled"""
		# Cancel related journal entry
		pass