import frappe
import json
import os

# Direct monkey patching approach
def monkey_patch_chart_functions():
    """Monkey patch chart of accounts functions to support our custom template"""
    
    # Import the modules we need to patch
    from erpnext.accounts.doctype.account.chart_of_accounts import chart_of_accounts
    from erpnext.setup.doctype.company import company
    
    # Store original functions
    original_get_charts_for_country = chart_of_accounts.get_charts_for_country
    original_get_chart = chart_of_accounts.get_chart
    original_create_default_tax_template = company.Company.create_default_tax_template
    
    def custom_get_charts_for_country(country, with_standard=False):
        """Custom function to include our chart template in the list"""
        # Get the original charts
        charts = original_get_charts_for_country(country, with_standard)
        
        # Add our custom template if not already present
        if "Holding Company Template" not in charts:
            charts.append("Holding Company Template")
        
        return charts
    
    def custom_get_chart(chart_template=None, existing_company=None):
        """Override the original get_chart function to handle our custom template"""
        
        if chart_template == "Holding Company Template":
            # Get the path to our template
            template_path = os.path.join(
                frappe.get_app_path("holding_company"), 
                "templates", 
                "chart_of_accounts", 
                "chart_of_accounts_template.json"
            )
            
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                    return template_data.get("tree")
            return None
        
        # For all other templates, use the original function
        return original_get_chart(chart_template, existing_company)
    
    def custom_create_default_tax_template(self):
        """Skip tax template creation for our custom chart template to avoid IndexError"""
        if hasattr(self, 'chart_of_accounts') and self.chart_of_accounts == "Holding Company Template":
            # Skip automatic tax template creation for our custom template
            return
        
        # For all other templates, use the original function
        return original_create_default_tax_template(self)
    
    # Make them whitelisted first
    custom_get_charts_for_country = frappe.whitelist()(custom_get_charts_for_country)
    custom_get_chart = frappe.whitelist()(custom_get_chart)
    
    # Apply monkey patches
    chart_of_accounts.get_charts_for_country = custom_get_charts_for_country
    chart_of_accounts.get_chart = custom_get_chart
    company.Company.create_default_tax_template = custom_create_default_tax_template

# Apply monkey patches when module is imported
monkey_patch_chart_functions()