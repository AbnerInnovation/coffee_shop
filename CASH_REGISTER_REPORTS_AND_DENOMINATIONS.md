# Cash Register: Reports and Denomination Counting Features

This document describes the newly implemented features for the Cash Register module: **Detailed Reports** and **Cash Drawer Denomination Counting**.

## Features Implemented

### 1. Detailed Reports (Daily/Weekly Summaries)

#### Backend Implementation

**New Schemas** (`backend/app/schemas/cash_register.py`):
- `WeeklySummaryReport`: Aggregates data from multiple sessions over a week
- `ReportDateRange`: Query parameters for filtering reports by date range

**New Service Functions** (`backend/app/services/cash_register.py`):
- `get_daily_summary_reports()`: Retrieves daily summary reports within a date range
- `get_weekly_summary()`: Generates weekly summary aggregating multiple sessions

**New API Endpoints** (`backend/app/api/routers/cash_register.py`):
- `GET /cash-register/reports/daily-summaries`: Get daily summary reports with optional date filtering
  - Query params: `start_date`, `end_date`, `skip`, `limit`
- `GET /cash-register/reports/weekly-summary`: Generate weekly summary report
  - Query params: `start_date`, `end_date`
  - Defaults to last 7 days if no dates provided

#### Frontend Implementation

**New Component** (`frontend/src/components/ReportsView.vue`):
- Tab-based interface for viewing different report types
- Date range filtering with start/end date pickers
- Two report views:
  - **Daily Summaries**: Shows individual session reports with metrics
  - **Weekly Summary**: Aggregated view of all sessions in the period

**Features**:
- Visual cards showing key metrics (sales, refunds, tips, expenses)
- Payment method breakdown (cash, card, digital, other)
- Net cash flow calculation
- Average session value for weekly reports
- Responsive grid layout

**Service Methods** (`frontend/src/services/cashRegisterService.ts`):
- `getDailySummaries(startDate?, endDate?)`: Fetch daily summary reports
- `getWeeklySummary(startDate?, endDate?)`: Fetch weekly summary report

### 2. Cash Drawer Denomination Counting (Mexican Pesos)

#### Backend Implementation

**New Schemas** (`backend/app/schemas/cash_register.py`):
- `DenominationCount`: Tracks count of each MXN bill/coin denomination
  - Bills: $1000, $500, $200, $100, $50, $20
  - Coins: $20, $10, $5, $2, $1, $0.50
  - `calculate_total()`: Method to compute total from denominations
- `SessionCloseWithDenominations`: Extended close session data with denominations
- `CutWithDenominations`: Cut data with denomination tracking

**New Service Function** (`backend/app/services/cash_register.py`):
- `close_session_with_denominations()`: Close session with optional denomination breakdown
  - Automatically calculates actual balance from denominations
  - Stores denomination data in session notes

**New API Endpoint** (`backend/app/api/routers/cash_register.py`):
- `PATCH /cash-register/sessions/{session_id}/close-with-denominations`: Close session with denomination counting

#### Frontend Implementation

**New Component** (`frontend/src/components/DenominationCounter.vue`):
- Interactive denomination counting interface for Mexican Pesos
- Separate sections for bills ($1000, $500, $200, $100, $50, $20) and coins ($20, $10, $5, $2, $1, $0.50)
- Real-time calculation showing:
  - Individual denomination totals
  - Overall total amount in MXN
- Two-way binding with parent component

**Features**:
- Number inputs for each denomination
- Automatic total calculation on input change
- Shows subtotal for each denomination type
- Clean, organized layout with dark mode support

**Updated Modal** (`frontend/src/views/CashRegisterView.vue`):
- Close Session Modal now includes:
  - Checkbox to toggle denomination counting
  - Embedded `DenominationCounter` component when enabled
  - Automatic balance calculation from denominations
  - Falls back to manual balance input when disabled

**Service Method** (`frontend/src/services/cashRegisterService.ts`):
- `closeSessionWithDenominations()`: Close session with denomination data

## Usage

### Viewing Reports

1. Navigate to Cash Register view
2. Click on the **Reports** tab
3. Select report type (Daily Summaries or Weekly Summary)
4. Choose date range using the date pickers
5. Click **Filter** to load reports
6. View detailed metrics and payment breakdowns

### Using Denomination Counting

1. Open Cash Register session
2. When ready to close, click **Close** button
3. In the close modal, check **"Count denominations"**
4. Enter the count for each bill and coin denomination
5. The total is automatically calculated
6. Add optional notes
7. Click **Save** to close the session

The denomination data is stored with the session and can be reviewed later.

## Benefits

### Reports Feature
- **Historical Analysis**: View performance over time
- **Trend Identification**: Compare daily vs weekly patterns
- **Payment Insights**: Understand customer payment preferences
- **Financial Planning**: Use average session values for forecasting

### Denomination Counting
- **Accuracy**: Reduces counting errors by breaking down by denomination
- **Audit Trail**: Complete record of cash drawer contents
- **Reconciliation**: Easier to identify discrepancies
- **Training**: Helps new staff learn proper cash handling

## Technical Notes

### Database
- No new tables required
- Denomination data stored as JSON in session notes
- Reports use existing `cash_register_reports` table

### API Compatibility
- All new endpoints are backward compatible
- Existing close session endpoint still works
- Denomination counting is optional

### Performance
- Reports use indexed queries on `generated_at` field
- Weekly summaries aggregate in-memory (suitable for typical volumes)
- Consider caching for high-traffic scenarios

## Testing Checklist

- [ ] Daily summaries load correctly with date filtering
- [ ] Weekly summary aggregates multiple sessions accurately
- [ ] Denomination counter calculates totals correctly
- [ ] Session closes successfully with denomination data
- [ ] Session closes successfully without denomination data (backward compatibility)
- [ ] Reports display properly in both light and dark modes
- [ ] Date range filtering works as expected
- [ ] Payment breakdown shows correct values

## Future Enhancements

Potential improvements:
- Export reports to PDF/Excel
- Graphical charts for trend visualization
- Denomination counting for "Cut" operations
- Preset denomination templates (e.g., standard drawer setup)
- Comparison reports (this week vs last week)
- Automated discrepancy alerts
