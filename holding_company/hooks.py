app_name = "holding_company"
app_title = "Holding Company"
app_publisher = "WIN BORN HOLDING"
app_description = "Investments & Dividends Management, Loans Management, Payment Processors Management, Multi Companies & Child Companies Management with Abbr at starting of Serial Number for Frappe."
app_email = "admin@winbornholding.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "holding_company",
# 		"logo": "/assets/holding_company/logo.png",
# 		"title": "Holding Company",
# 		"route": "/holding_company",
# 		"has_permission": "holding_company.api.permission.has_app_permission"
# 	}
# ]

# Fixtures
# --------
fixtures = [
	"Custom Field",
	"Property Setter", 
	"Print Format",
	"Document Naming Settings",
	"Workspace",
	"List View Settings"
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/holding_company/css/holding_company.css"
# app_include_js = "/assets/holding_company/js/holding_company.js"

# include js, css files in header of web template
# web_include_css = "/assets/holding_company/css/holding_company.css"
# web_include_js = "/assets/holding_company/js/holding_company.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "holding_company/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	# Payment Processors Module
	"Funds Hold": "payment_processors/doctype/funds_hold/funds_hold.js",
	"Funds Payout": "payment_processors/doctype/funds_payout/funds_payout.js",
	"Funds Callback": "payment_processors/doctype/funds_callback/funds_callback.js",
	
	# Investments Module
	"Investee": "investments/doctype/investee/investee.js",
	"Investee Accounts": "investments/doctype/investee_accounts/investee_accounts.js",
	"Investment Application": "investments/doctype/investment_application/investment_application.js",
	"Investment": "investments/doctype/investment/investment.js",
	"Investment Return": "investments/doctype/investment_return/investment_return.js",
	"Borrower": "investments/doctype/borrower/borrower.js",
	"Borrower Accounts": "investments/doctype/borrower_accounts/borrower_accounts.js",
	"Lending Application": "investments/doctype/lending_application/lending_application.js",
	"Lending": "investments/doctype/lending/lending.js",
	"Lending Repayment": "investments/doctype/lending_repayment/lending_repayment.js",
	
	# Liabilities Module
	"Company Loan Application": "liabilities/doctype/company_loan_application/company_loan_application.js",
	"Company Loan": "liabilities/doctype/company_loan/company_loan.js",
	"Company Loan Repayment": "liabilities/doctype/company_loan_repayment/company_loan_repayment.js",
	"Lender": "liabilities/doctype/lender/lender.js",
	"Lender Accounts": "liabilities/doctype/lender_accounts/lender_accounts.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "holding_company/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "holding_company.utils.jinja_methods",
# 	"filters": "holding_company.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "holding_company.install.before_install"
# after_install = "holding_company.overrides.apply_patches"

# Uninstallation
# ------------

# before_uninstall = "holding_company.uninstall.before_uninstall"
# after_uninstall = "holding_company.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "holding_company.utils.before_app_install"
# after_app_install = "holding_company.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "holding_company.utils.before_app_uninstall"
# after_app_uninstall = "holding_company.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "holding_company.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"holding_company.tasks.all"
# 	],
# 	"daily": [
# 		"holding_company.tasks.daily"
# 	],
# 	"hourly": [
# 		"holding_company.tasks.hourly"
# 	],
# 	"weekly": [
# 		"holding_company.tasks.weekly"
# 	],
# 	"monthly": [
# 		"holding_company.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "holding_company.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "holding_company.event.get_events"
# }

# Whitelisted Methods
# -------------------
# whitelisted_methods = []
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "holding_company.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["holding_company.overrides.apply_patches"]
# after_request = ["holding_company.utils.after_request"]

# Job Events
# ----------
# before_job = ["holding_company.utils.before_job"]
# after_job = ["holding_company.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"holding_company.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

