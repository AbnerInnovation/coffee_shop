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
 * Calculate session duration from opened_at timestamp
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
 * Calculate total expenses from transactions
 */
export function calculateSessionExpenses(transactions: Transaction[]): number {
  return transactions
    .filter(t => t.transaction_type === 'expense')
    .reduce((sum, t) => sum + Math.abs(t.amount || 0), 0);
}

/**
 * Calculate current balance from initial balance and transactions
 */
export function calculateCurrentBalance(initialBalance: number, transactions: Transaction[]): number {
  const totalTransactions = transactions.reduce((sum, t) => sum + (t.amount || 0), 0);
  return initialBalance + totalTransactions;
}

/**
 * Calculate cut report from transactions
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
 * Calculate payment breakdown by method
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
 * Format date string to locale string
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
 * Translate transaction description
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
 * Translate transaction type
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
 * Translate payment method
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
 * Get CSS classes for payment method badge
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
 * Create initial empty denominations object
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
