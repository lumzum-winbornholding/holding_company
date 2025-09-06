import frappe
import json
import os

# Store original functions before patching
_original_get_charts_for_country = None
_original_get_chart = None

def _store_originals():
    """Store original functions before patching"""
    global _original_get_charts_for_country, _original_get_chart
    if _original_get_charts_for_country is None:
        from erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts import get_charts_for_country, get_chart
        _original_get_charts_for_country = get_charts_for_country
        _original_get_chart = get_chart

@frappe.whitelist()
def get_charts_for_country(country, with_standard=False):
    """Override to add our chart template"""
    # Get original charts from ERPNext
    charts = _original_get_charts_for_country(country, with_standard)
    
    # Add our chart
    charts.append("Holding Company")
    
    return charts


@frappe.whitelist()
def get_chart(chart_template, existing_company=None):
    """Override to load our chart template"""
    if chart_template == "Holding Company":
        chart_path = frappe.get_app_path("holding_company", "templates", "chart_of_accounts", "chart_of_accounts_template.json")
        with open(chart_path, "r") as f:
            chart_data = json.load(f)
            return chart_data.get("tree", {})  # Return only the tree portion
    
    # Use original for other charts
    return _original_get_chart(chart_template, existing_company)


def apply_patches():
    """Apply the patches"""
    _store_originals()
    import erpnext.accounts.doctype.account.chart_of_accounts.chart_of_accounts as chart_module
    chart_module.get_charts_for_country = get_charts_for_country
    chart_module.get_chart = get_chart


# Apply patches on import
apply_patches()