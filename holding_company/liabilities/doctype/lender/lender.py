import frappe
from frappe import _
from frappe.model.document import Document
from frappe.contacts.address_and_contact import (
	load_address_and_contact,
	delete_contact_and_address
)


class Lender(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self, "lender")

	def on_trash(self):
		delete_contact_and_address("Lender", self.name)


@frappe.whitelist()
def make_contact(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	def postprocess(source, target):
		target.company_name = source.lender_name
		target.append("links", {
			"link_doctype": "Lender",
			"link_name": source.name
		})
	
	return get_mapped_doc("Lender", source_name, {
		"Lender": {
			"doctype": "Contact"
		}
	}, target_doc, postprocess)


@frappe.whitelist()
def make_address(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	def postprocess(source, target):
		target.address_title = source.lender_name
		target.append("links", {
			"link_doctype": "Lender",
			"link_name": source.name
		})
	
	return get_mapped_doc("Lender", source_name, {
		"Lender": {
			"doctype": "Address"
		}
	}, target_doc, postprocess)