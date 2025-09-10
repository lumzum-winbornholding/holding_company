# Holding Company App - ERPNext Custom Application

## Project Overview
**App Name**: holding_company  
**Developer**: WIN BORN HOLDING  
**Purpose**: Investments & Dividends Management, Loans Management, Payment Processors Management, Multi Companies & Child Companies Management with Abbr at starting of Serial Number for Frappe.

## Environment Context
- **Platform**: ERPNext/Frappe Framework
- **Docker Container**: Yes (frappe-bench environment)
- **Working Directory**: `/home/frappe/frappe-bench/apps/holding_company`

## App Structure

```
apps/holding_company/
├── holding_company/
│   ├── config/           # App configuration
│   ├── fixtures/         # Fixtures data
│   ├── holding_company/  # Main module (master data, settings)
│   ├── investments/      # Investment management module ⭐ CURRENT FOCUS
│   ├── liabilities/      # Liabilities management module
│   ├── payment_processors/ # Payment processing module (REFERENCE MODEL)
│   ├── public/          # Static assets
│   ├── templates/       # Web templates
│   ├── hooks.py         # App hooks and configuration
│   ├── modules.txt      # Module list
│   └── overrides.py     # Framework overrides
```

## Modules Overview

### 1. Payment Processors Module (Reference Implementation)
**Status**: ✅ Completed - Use as template for other modules

**DocTypes**:
- `Funds Hold` - Holds funds with journal entries
- `Funds Payout` - Processes fund payouts  
- `Funds Callback` - Handles payment callbacks

**Implementation Pattern**:
- **Client Scripts** (`.js`): Form behaviors, field calculations, auto-population
- **Server Scripts** (`.py`): Document lifecycle, business logic, journal entry creation
- **JSON Schema** (`.json`): DocType definitions and field configurations

**Key Features from Funds Hold**:
```javascript
// Client Script (funds_hold.js)
- Form refresh handlers
- Field calculations (transaction fees, VAT, net amounts)
- Auto-population from Payment Entry and Mode of Payment
- Dynamic account field mapping
```

```python
# Server Script (funds_hold.py) 
- Document lifecycle hooks (on_submit, on_cancel, on_amend)
- Automatic Journal Entry creation/cancellation
- Error handling and logging
- Business logic validation
```

### 2. Investments Module (Current Focus)
**Status**: 🔄 In Development - Needs client/server scripts

**Current DocTypes**:
- `Investee` ✅ (has basic .js/.py files)
- `Investee Accounts`
- `Investment` (only .json exists)
- `Investment Application`
- `Investment Return`
- `Borrower`
- `Borrower Accounts`
- `Lending`
- `Lending Application`
- `Lending Repayment`

**Current State**:
- Most DocTypes have only JSON schema files
- `Investee` has client/server scripts but minimal functionality
- Need to implement full client/server scripts following Payment Processors pattern

### 3. Liabilities Module
**Status**: 📝 Defined but minimal implementation

### 4. Holding Company Module (Main)
**Status**: 📝 Master data and settings

## Hooks Configuration (hooks.py)

**Key Configurations**:
```python
# Client Scripts Registration
doctype_js = {
    "Funds Hold": "payment_processors/doctype/funds_hold/funds_hold.js",
    "Funds Payout": "payment_processors/doctype/funds_payout/funds_payout.js", 
    "Funds Callback": "payment_processors/doctype/funds_callback/funds_callback.js",
    "Investee": "investments/doctype/investee/investee.js"  # ⭐ Add more here
}

# Fixtures for data migration
fixtures = [
    "Custom Field",
    "Property Setter", 
    "Print Format",
    "Document Naming Settings",
    "Workspace"
]
```

## Development Workflow Pattern

### For Each DocType in Investments Module:

1. **JSON Schema** (`.json`) - Already exists
   - Field definitions, permissions, naming rules

2. **Server Script** (`.py`) - TO BE IMPLEMENTED
   ```python
   # Follow pattern from funds_hold.py
   class DocTypeName(Document):
       def on_submit(self):
           # Business logic on submit
       
       def on_cancel(self):
           # Cleanup on cancellation
           
       def validate(self):
           # Validation logic
   ```

3. **Client Script** (`.js`) - TO BE IMPLEMENTED  
   ```javascript
   // Follow pattern from funds_hold.js
   frappe.ui.form.on('DocType Name', {
       refresh: function(frm) {
           // Form setup logic
       },
       
       field_name: function(frm) {
           // Field change handlers
       }
   });
   ```

4. **Register in hooks.py**
   ```python
   doctype_js = {
       "New DocType": "investments/doctype/new_doctype/new_doctype.js"
   }
   ```

## Next Steps for Investments Module

1. **Priority DocTypes for Client/Server Scripts**:
   - `Investment` - Core investment tracking
   - `Investment Application` - Investment requests
   - `Investment Return` - ROI calculations
   - `Borrower` - Loan recipients
   - `Lending` - Loan management
   - `Lending Repayment` - Payment tracking

2. **Implementation Approach**:
   - Use Payment Processors module as reference
   - Implement server scripts for business logic and journal entries
   - Create client scripts for form behaviors and calculations
   - Add hooks.py entries for each new script

3. **Common Patterns to Implement**:
   - Automatic journal entry creation/cancellation
   - Field calculations and validations
   - Integration with ERPNext accounting
   - Dynamic field population
   - Document lifecycle management

## Commands for Development

```bash
# Navigate to app directory
cd /home/frappe/frappe-bench/apps/holding_company

# Install/update app
bench --site [site-name] install-app holding_company
bench --site [site-name] migrate

# Development server
bench start

# View logs
bench --site [site-name] console
```

## File Structure for New DocType Scripts

```
investments/doctype/investment/
├── __init__.py
├── investment.json     ✅ (exists)
├── investment.js       ❌ (to create)
└── investment.py       ❌ (to create)
```

Remember: Always follow the established patterns from Payment Processors module for consistency and maintainability.