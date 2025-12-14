/**
 * Cash Register Helper Functions
 * Pure functions for transformations, calculations, and formatting
 * Implements Single Responsibility Principle
 */

// Type for translation function
type TranslateFunction = (key: string, params?: any) => string;

/**
 * Transaction type for type safety
 */
export interface Transaction {
  id: number;
  amount: number;
  description: string;
  transaction_type: string;
  payment_method?: string;
  category?: string;
  created_at: string;
}

/**
 * Session type
 */
export interface CashRegisterSession {
  id: number;
  session_number: number;
  opened_at: string;
  closed_at?: string;
  initial_balance: number;
  final_balance?: number;
}

/**
 * Cut report type
 */
export interface CutReport {
  total_sales: number;
  total_refunds: number;
  total_tips: number;
  total_expenses: number;
  total_transactions: number;
  net_cash_flow: number;
}

/**
 * Denomination breakdown type
 */
export interface Denominations {
  bills_1000: number;
  bills_500: number;
  bills_200: number;
  bills_100: number;
  bills_50: number;
  bills_20: number;
  coins_20: number;
  coins_10: number;
  coins_5: number;
  coins_2: number;
  coins_1: number;
  coins_50_cent: number;
}

/**
 * Calculates the duration of a cash register session
 * 
 * @param openedAt - ISO timestamp when session was opened
 * @param currentTime - Current time for comparison
 * @returns Formatted duration string (e.g., '2h 35m')
 * 
 * @example
 * ```typescript
 * const duration = calculateSessionDuration('2025-11-14T09:00:00', new Date());
 * // Returns: '2h 35m'
 * ```
 */
export function calculateSessionDuration(openedAt: string, currentTime: Date): string {
  if (!openedAt) return '0h 0m';
  
  const openedDate = new Date(openedAt);
  const diffMs = currentTime.getTime() - openedDate.getTime();
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  return `${hours}h ${minutes}m`;
}

/**
 * Calculates total expenses from transaction list
 * Only counts transactions with type 'expense'
 * 
 * @param transactions - Array of transactions
 * @returns Total expense amount (always positive)
 * 
 * @example
 * ```typescript
 * const expenses = calculateSessionExpenses(transactions);
 * // Returns: 150.50
 * ```
 */
export function calculateSessionExpenses(transactions: Transaction[]): number {
  return transactions
    .filter(t => t.transaction_type === 'expense')
    .reduce((sum, t) => sum + Math.abs(t.amount || 0), 0);
}

/**
 * Calculates total sales amount from transaction list
 * Only counts transactions with type 'sale'
 * 
 * @param transactions - Array of transactions
 * @returns Total sales amount
 * 
 * @example
 * ```typescript
 * const salesAmount = calculateSessionSales(transactions);
 * // Returns: 5000.00
 * ```
 */
export function calculateSessionSales(transactions: Transaction[]): number {
  return transactions
    .filter(t => t.transaction_type === 'sale')
    .reduce((sum, t) => sum + (t.amount || 0), 0);
}

/**
 * Counts number of sale transactions
 * 
 * @param transactions - Array of transactions
 * @returns Count of sale transactions
 * 
 * @example
 * ```typescript
 * const salesCount = calculateSalesCount(transactions);
 * // Returns: 45
 * ```
 */
export function calculateSalesCount(transactions: Transaction[]): number {
  return transactions.filter(t => t.transaction_type === 'sale').length;
}

/**
 * Counts number of expense transactions
 * 
 * @param transactions - Array of transactions
 * @returns Count of expense transactions
 * 
 * @example
 * ```typescript
 * const expensesCount = calculateExpensesCount(transactions);
 * // Returns: 8
 * ```
 */
export function calculateExpensesCount(transactions: Transaction[]): number {
  return transactions.filter(t => t.transaction_type === 'expense').length;
}

/**
 * Calculates current balance from initial balance and all transactions
 * 
 * Formula: initial_balance + sum(all_transactions)
 * - Positive amounts increase balance (sales, tips)
 * - Negative amounts decrease balance (expenses, refunds)
 * 
 * @param initialBalance - Starting balance when session opened
 * @param transactions - Array of all transactions
 * @returns Current calculated balance
 * 
 * @example
 * ```typescript
 * const balance = calculateCurrentBalance(1000, transactions);
 * // Returns: 1450.75
 * ```
 */
export function calculateCurrentBalance(initialBalance: number, transactions: Transaction[]): number {
  const totalTransactions = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
  return initialBalance + totalTransactions;
}

/**
 * Generates a comprehensive cut report from transactions
 * 
 * Calculates:
 * - Total sales (type: 'sale')
 * - Total refunds (type: 'refund' or 'cancellation')
 * - Total tips (type: 'tip')
 * - Total expenses (type: 'expense')
 * - Net cash flow (sales - refunds + tips - expenses)
 * 
 * @param transactions - Array of transactions to analyze
 * @returns Cut report with all calculated totals
 * 
 * @example
 * ```typescript
 * const report = calculateCutReport(transactions);
 * // Returns: {
 * //   total_sales: 5000,
 * //   total_refunds: 200,
 * //   total_tips: 300,
 * //   total_expenses: 150,
 * //   total_transactions: 45,
 * //   net_cash_flow: 4950
 * // }
 * ```
 */
export function calculateCutReport(transactions: Transaction[]): CutReport {
  const totalSales = transactions
    .filter(t => t.transaction_type === 'sale')
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const totalRefunds = transactions
    .filter(t => t.transaction_type === 'refund' || t.transaction_type === 'cancellation')
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const totalTips = transactions
    .filter(t => t.transaction_type === 'tip')
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const totalExpenses = transactions
    .filter(t => t.transaction_type === 'expense')
    .reduce((sum, t) => sum + Math.abs(t.amount || 0), 0);

  const netCashFlow = totalSales - totalRefunds + totalTips - totalExpenses;

  return {
    total_sales: totalSales,
    total_refunds: totalRefunds,
    total_tips: totalTips,
    total_expenses: totalExpenses,
    total_transactions: transactions.length,
    net_cash_flow: netCashFlow
  };
}

/**
 * Calculates payment totals grouped by payment method
 * Only counts positive amounts (sales, not refunds)
 * 
 * @param transactions - Array of transactions
 * @returns Object with totals for each payment method
 * 
 * @example
 * ```typescript
 * const breakdown = calculatePaymentBreakdown(transactions);
 * // Returns: {
 * //   cash: 2500,
 * //   card: 1800,
 * //   digital: 700,
 * //   other: 0
 * // }
 * ```
 */
export function calculatePaymentBreakdown(transactions: Transaction[]) {
  const cashTotal = transactions
    .filter(t => t.payment_method?.toUpperCase() === 'CASH' && t.amount > 0)
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const cardTotal = transactions
    .filter(t => t.payment_method?.toUpperCase() === 'CARD' && t.amount > 0)
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const digitalTotal = transactions
    .filter(t => t.payment_method?.toUpperCase() === 'DIGITAL' && t.amount > 0)
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  const otherTotal = transactions
    .filter(t => t.payment_method?.toUpperCase() === 'OTHER' && t.amount > 0)
    .reduce((sum, t) => sum + (t.amount || 0), 0);

  return {
    cash: cashTotal,
    card: cardTotal,
    digital: digitalTotal,
    other: otherTotal
  };
}

/**
 * Formats transaction date to localized string
 * 
 * @param dateString - ISO date string
 * @returns Localized date and time string
 * 
 * @example
 * ```typescript
 * formatTransactionDate('2025-11-14T09:30:00');
 * // Returns: '14/11/2025, 09:30:00' (locale-dependent)
 * ```
 */
export function formatTransactionDate(dateString: string): string {
  if (!dateString) return 'No date';
  try {
    return new Date(dateString).toLocaleString();
  } catch (error) {
    console.error('Error formatting date:', dateString, error);
    return 'Invalid date';
  }
}

/**
 * Translates transaction description to current language
 * Handles special patterns like order payments
 * 
 * @param description - Raw description from API
 * @param t - i18n translation function
 * @returns Translated description
 * 
 * @example
 * ```typescript
 * translateDescription('Payment for order #123', t);
 * // Returns: 'Pago de orden #123' (in Spanish)
 * ```
 */
export function translateDescription(description: string, t: TranslateFunction): string {
  // Translate "Payment for order #X" pattern
  const orderPaymentMatch = description.match(/Payment for order #(\d+)/i);
  if (orderPaymentMatch) {
    return t('app.views.cashRegister.paymentForOrder', { orderNumber: orderPaymentMatch[1] });
  }
  return description;
}

/**
 * Translates transaction type code to display label
 * 
 * @param type - Transaction type code ('sale', 'refund', etc.)
 * @param t - i18n translation function
 * @returns Translated type label
 * 
 * @example
 * ```typescript
 * translateTransactionType('sale', t);
 * // Returns: 'Venta' (in Spanish)
 * ```
 */
export function translateTransactionType(type: string, t: TranslateFunction): string {
  const typeMap: Record<string, string> = {
    'sale': t('app.views.cashRegister.typeSale'),
    'refund': t('app.views.cashRegister.typeRefund'),
    'cancellation': t('app.views.cashRegister.typeCancellation'),
    'tip': t('app.views.cashRegister.typeTip'),
    'manual_add': t('app.views.cashRegister.typeManualAdd'),
    'manual_withdraw': t('app.views.cashRegister.typeManualWithdraw'),
    'expense': t('app.views.cashRegister.typeExpense')
  };
  return typeMap[type] || type;
}

/**
 * Translates payment method code to display label
 * 
 * @param method - Payment method code ('cash', 'card', etc.)
 * @param t - i18n translation function
 * @returns Translated method label
 * 
 * @example
 * ```typescript
 * translatePaymentMethod('cash', t);
 * // Returns: 'Efectivo' (in Spanish)
 * ```
 */
export function translatePaymentMethod(method: string, t: TranslateFunction): string {
  const methodMap: Record<string, string> = {
    'cash': t('app.views.cashRegister.cash') || 'Cash',
    'card': t('app.views.cashRegister.card') || 'Card',
    'digital': t('app.views.cashRegister.digital') || 'Digital',
    'other': t('app.views.cashRegister.other') || 'Other'
  };
  return methodMap[method?.toLowerCase()] || method;
}

/**
 * Gets Tailwind CSS classes for payment method badge
 * Returns color-coded classes with dark mode support
 * 
 * @param paymentMethod - Payment method code
 * @returns Tailwind CSS classes string
 * 
 * @example
 * ```typescript
 * const classes = getPaymentMethodBadgeClass('CASH');
 * // Returns: 'bg-green-100 dark:bg-green-900/30 text-green-700 ...'
 * ```
 */
export function getPaymentMethodBadgeClass(paymentMethod: string): string {
  const method = paymentMethod?.toUpperCase();
  switch (method) {
    case 'CASH':
      return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800';
    case 'CARD':
      return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-800';
    case 'DIGITAL':
      return 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800';
    case 'OTHER':
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600';
    default:
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
  }
}

/**
 * Creates an empty denominations object with all values set to 0
 * Used for initializing denomination counting forms
 * 
 * @returns Denominations object with all counts at 0
 * 
 * @example
 * ```typescript
 * const denoms = createEmptyDenominations();
 * // Returns: { bills_1000: 0, bills_500: 0, ... }
 * ```
 */
export function createEmptyDenominations(): Denominations {
  return {
    bills_1000: 0,
    bills_500: 0,
    bills_200: 0,
    bills_100: 0,
    bills_50: 0,
    bills_20: 0,
    coins_20: 0,
    coins_10: 0,
    coins_5: 0,
    coins_2: 0,
    coins_1: 0,
    coins_50_cent: 0
  };
}
