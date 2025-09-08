import frappe
from frappe import _
from frappe.model.document import Document
from frappe.contacts.address_and_contact import (
	load_address_and_contact,
	delete_contact_and_address
)


class Investee(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self, "investee")

	def on_trash(self):
		delete_contact_and_address("Investee", self.name)


@frappe.whitelist()
def make_contact(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	return get_mapped_doc("Investee", source_name, {
		"Investee": {
			"doctype": "Contact",
			"field_map": {
				"investee_name": "company_name",
				"name": "investee"
			}
		}
	}, target_doc)


@frappe.whitelist()
def make_address(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	return get_mapped_doc("Investee", source_name, {
		"Investee": {
			"doctype": "Address",
			"field_map": {
				"investee_name": "address_title",
				"name": "investee"
			}
		}
	}, target_doc)