# Cash Register Expense Tracking Guide

## Overview
This guide explains how to use the expense tracking feature in cash register sessions.

## Features Added

### Backend Changes

1. **New Transaction Type**: Added `EXPENSE` to the `TransactionType` enum
   - Location: `backend/app/models/cash_register.py` and `backend/app/schemas/cash_register.py`

2. **Expense Schema**: Created `ExpenseCreate` schema for validating expense data
   - Location: `backend/app/schemas/cash_register.py`
   - Fields:
     - `amount`: Positive float (required)
     - `description`: String (required)
     - `category`: Optional string for categorization

3. **Service Function**: Added `add_expense_to_session()` function
   - Location: `backend/app/services/cash_register.py`
   - Validates session is open
   - Creates negative transaction to reduce cash balance
   - Supports optional expense categories

4. **API Endpoint**: `POST /api/cash-register/sessions/{session_id}/expenses`
   - Location: `backend/app/api/routers/cash_register.py`
   - Requires authentication
   - Returns created transaction

### Frontend Changes

1. **Service Method**: Added `addExpense()` to cashRegisterService
   - Location: `frontend/src/services/cashRegisterService.ts`

2. **UI Component**: Added expense modal to CashRegisterView
   - Location: `frontend/src/views/CashRegisterView.vue`
   - Features:
     - Amount input
     - Description input
     - Category dropdown (optional)
     - Form validation

3. **Translations**: Added expense-related i18n keys
   - Location: `frontend/src/locales/en.json`
   - Keys under `app.views.cashRegister.*`

### Database Migration

- File: `backend/migrations/versions/add_expense_transaction_type.py`
- Adds 'expense' value to the `transaction_type` enum
- **Note**: Uses MySQL-specific `ALTER TABLE ... MODIFY COLUMN` syntax (not PostgreSQL's `ALTER TYPE`)

## How to Use

### Running the Migration

```bash
cd backend
alembic upgrade head
```

### Adding an Expense via UI

1. Navigate to Cash Register view
2. Ensure a session is open
3. Click "Add Expense" button (orange)
4. Fill in:
   - Amount (required, positive number)
   - Description (required, e.g., "Coffee beans purchase")
   - Category (optional, e.g., "Supplies", "Utilities", "Maintenance")
5. Click "Save"

### Adding an Expense via API

```bash
POST /api/cash-register/sessions/{session_id}/expenses
Content-Type: application/json
Authorization: Bearer <token>

{
  "amount": 50.00,
  "description": "Coffee beans purchase",
  "category": "supplies"
}
```

### Expense Categories

Available categories:
- **Supplies**: Office or store supplies
- **Utilities**: Electricity, water, internet, etc.
- **Maintenance**: Repairs and maintenance
- **Inventory**: Stock purchases
- **Other**: Miscellaneous expenses

## Technical Details

### Transaction Behavior

- Expenses are recorded as **negative transactions** in the cash register
- They reduce the expected balance of the session
- Format: `[Category] Description` (if category provided)
- Example: `[supplies] Coffee beans purchase`

### Validation Rules

1. Amount must be positive (converted to negative internally)
2. Description is required and cannot be empty
3. Session must be in OPEN status
4. User must be authenticated

### Balance Calculation

The current balance includes all transactions:
```
Current Balance = Initial Balance + Sales + Tips - Refunds - Expenses
```

### Reporting

Expenses are included in:
- Transaction lists
- Session summaries
- Daily reports
- Cash difference calculations

## Example Workflow

1. **Open Session**: Start with $100 initial balance
2. **Record Sales**: +$250 from customer orders
3. **Add Expense**: -$50 for coffee beans
4. **Add Expense**: -$20 for cleaning supplies
5. **Current Balance**: $100 + $250 - $50 - $20 = $280
6. **Close Session**: Count actual cash and compare to expected $280

## Notes

- Expenses can only be added to OPEN sessions
- Once a session is closed, no more expenses can be added
- All expenses are tracked with timestamps and user information
- Categories help with expense reporting and analysis
