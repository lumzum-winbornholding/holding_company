import frappe
from frappe import _
from frappe.model.document import Document
from frappe.contacts.address_and_contact import (
	load_address_and_contact,
	delete_contact_and_address
)


class Borrower(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self, "borrower")

	def on_trash(self):
		delete_contact_and_address("Borrower", self.name)


@frappe.whitelist()
def make_contact(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	def postprocess(source, target):
		target.company_name = source.borrower_name
		target.append("links", {
			"link_doctype": "Borrower",
			"link_name": source.name
		})
	
	return get_mapped_doc("Borrower", source_name, {
		"Borrower": {
			"doctype": "Contact"
		}
	}, target_doc, postprocess)


@frappe.whitelist()
def make_address(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	def postprocess(source, target):
		target.address_title = source.borrower_name
		target.append("links", {
			"link_doctype": "Borrower",
			"link_name": source.name
		})
	
	return get_mapped_doc("Borrower", source_name, {
		"Borrower": {
			"doctype": "Address"
		}
	}, target_doc, postprocess)