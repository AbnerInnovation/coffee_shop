import { type Ref } from 'vue';
import { useI18n } from 'vue-i18n';
import cashRegisterService from '@/services/cashRegisterService';
import { useToast } from '@/composables/useToast';
import {
  calculateCutReport,
  calculatePaymentBreakdown
} from '@/utils/cashRegisterHelpers';
import { handleError } from '@/utils/errorTranslator';

/**
 * Composable for handling cash register modal operations
 * 
 * Manages all business logic for:
 * - Opening sessions with validation
 * - Closing sessions with denominations
 * - Adding expenses with validation
 * - Performing cuts with payment breakdown
 * 
 * @param currentSession - Ref to the current active session
 * @param openSessionService - Function to open a new session
 * @param closeSessionService - Function to close current session
 * @param addExpenseService - Function to add an expense
 * @param performCutService - Function to perform a cut
 * @param closeModals - Function to close all modals
 * @param setCutReport - Function to update cut report state
 * @param setPaymentBreakdown - Function to update payment breakdown state
 * 
 * @returns Object with all modal handler functions
 * 
 * @example
 * ```typescript
 * const {
 *   handleOpenSession,
 *   handleCloseSession,
 *   handleAddExpense,
 *   handlePerformCut,
 *   openCutModal
 * } = useCashRegisterHandlers(
 *   currentSession,
 *   openSession,
 *   closeSession,
 *   addExpense,
 *   performCut,
 *   closeModals,
 *   setCutReport,
 *   setPaymentBreakdown
 * );
 * ```
 */
export function useCashRegisterHandlers(
  currentSession: Ref<any>,
  openSessionService: (balance: number) => Promise<void>,
  closeSessionService: (balance: number, notes?: string, denominations?: any) => Promise<void>,
  addExpenseService: (amount: number, description: string, category?: string) => Promise<void>,
  performCutService: (data: any) => Promise<any>,
  closeModals: () => void,
  setCutReport: (report: any) => void,
  setPaymentBreakdown: (breakdown: any) => void,
  openCutModalBase: () => void
) {
  const { t } = useI18n();
  const toast = useToast();

  /**
   * Opens the cut modal and pre-populates it with current session data
   * Calculates cut report and payment breakdown from transactions
   */
  const openCutModal = async () => {
    openCutModalBase();

    if (currentSession.value) {
      try {
        const transactionsResponse = await cashRegisterService.getTransactions(currentSession.value.id);
        const txns = Array.isArray(transactionsResponse) ? transactionsResponse : transactionsResponse.data || [];

        // Calculate and set cut report
        const report = calculateCutReport(txns);
        setCutReport(report);

        // Calculate and set payment breakdown
        const breakdown = calculatePaymentBreakdown(txns);
        setPaymentBreakdown(breakdown);
      } catch (error) {
        console.error('Error loading cut report data:', error);
      }
    }
  };

  /**
   * Handles opening a new cash register session
   * Validates initial balance before proceeding
   * 
   * @param balance - Initial balance amount
   */
  const handleOpenSession = async (balance: number) => {
    if (!balance) {
      toast.showToast(t('app.views.cashRegister.initialBalanceRequired') || 'Initial balance is required', 'error');
      return;
    }

    try {
      await openSessionService(balance);
      closeModals();
      toast.showToast(t('app.views.cashRegister.sessionOpened') || 'Session opened successfully', 'success');
    } catch (error: any) {
      console.error('Error opening session:', error);
      const errorMessage = handleError(
        error, 
        t, 
        'cash_register',
        t('app.views.cashRegister.sessionOpenFailed') || 'Failed to open session'
      );
      toast.showToast(errorMessage, 'error');
    }
  };

  /**
   * Handles closing the current cash register session
   * Validates final balance and processes denomination counting if enabled
   * 
   * @param data - Object containing balance, notes, denomination settings
   * @param data.balance - Final balance amount
   * @param data.notes - Optional closing notes
   * @param data.useDenominations - Whether to use denomination counting
   * @param data.denominations - Denomination breakdown if enabled
   */
  const handleCloseSession = async (data: { 
    balance: number; 
    notes: string; 
    useDenominations: boolean; 
    denominations: any 
  }) => {
    if (!data.balance) {
      toast.showToast(t('app.views.cashRegister.finalBalanceRequired') || 'Final balance is required', 'error');
      return;
    }

    try {
      await closeSessionService(
        data.balance,
        data.notes || undefined,
        data.useDenominations ? data.denominations : undefined
      );
      closeModals();
      toast.showToast(t('app.views.cashRegister.sessionClosed') || 'Session closed successfully', 'success');
    } catch (error: any) {
      console.error('Error closing session:', error);
      toast.showToast(error.response?.data?.detail || 'Failed to close session', 'error');
    }
  };

  /**
   * Handles adding an expense to the current session
   * Validates amount, description, and active session before proceeding
   * 
   * @param data - Object containing expense details
   * @param data.amount - Expense amount (must be > 0)
   * @param data.description - Expense description (required)
   * @param data.category - Optional expense category
   */
  const handleAddExpense = async (data: { 
    amount: number; 
    description: string; 
    category: string 
  }) => {
    // Validate amount
    if (!data.amount || data.amount <= 0) {
      toast.showToast(t('app.views.cashRegister.expenseAmountRequired') || 'Expense amount is required', 'error');
      return;
    }

    // Validate description
    if (!data.description || data.description.trim() === '') {
      toast.showToast(t('app.views.cashRegister.expenseDescriptionRequired') || 'Expense description is required', 'error');
      return;
    }

    // Validate active session
    if (!currentSession.value) {
      toast.showToast(t('app.views.cashRegister.noActiveSession') || 'No active session', 'error');
      return;
    }

    try {
      await addExpenseService(data.amount, data.description, data.category || undefined);
      toast.showToast(t('app.views.cashRegister.expenseAdded') || 'Expense added successfully', 'success');
      closeModals();
    } catch (error: any) {
      console.error('Error adding expense:', error);
      toast.showToast(
        error.response?.data?.detail || 
        t('app.views.cashRegister.expenseFailed') || 
        'Failed to add expense', 
        'error'
      );
    }
  };

  /**
   * Handles performing a cut (partial cash count) during the session
   * Updates cut report with calculated totals
   * 
   * @param data - Object containing payment method amounts
   * @param data.cash - Cash amount
   * @param data.card - Card payment amount
   * @param data.digital - Digital payment amount
   * @param data.other - Other payment methods amount
   */
  const handlePerformCut = async (data: { 
    cash: number; 
    card: number; 
    digital: number; 
    other: number 
  }) => {
    if (!currentSession.value) return;

    try {
      const resultData = await performCutService(data);
      
      // Update cut report with results
      setCutReport({
        total_sales: resultData.total_sales || 0,
        total_refunds: resultData.total_refunds || 0,
        total_tips: resultData.total_tips || 0,
        total_expenses: resultData.total_expenses || 0,
        total_transactions: resultData.total_transactions || 0,
        net_cash_flow: resultData.net_cash_flow || 0
      });

      toast.showToast(t('app.views.cashRegister.cutSuccessful') || 'Cut performed successfully', 'success');
      closeModals();
    } catch (error: any) {
      console.error('Error performing cut:', error);
      toast.showToast(
        error.response?.data?.detail || 
        t('app.views.cashRegister.cutFailed') || 
        'Failed to perform cut', 
        'error'
      );
    }
  };

  return {
    openCutModal,
    handleOpenSession,
    handleCloseSession,
    handleAddExpense,
    handlePerformCut
  };
}
