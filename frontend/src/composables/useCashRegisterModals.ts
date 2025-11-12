import { ref } from 'vue';
import type { Transaction, CutReport, Denominations } from '@/utils/cashRegisterHelpers';
import { createEmptyDenominations } from '@/utils/cashRegisterHelpers';

/**
 * Composable for cash register modal management
 * Implements Single Responsibility Principle - only handles modal state
 */
export function useCashRegisterModals() {
  // Modal visibility state
  const openModalOpen = ref(false);
  const closeModalOpen = ref(false);
  const cutModalOpen = ref(false);
  const expenseModalOpen = ref(false);
  const deleteConfirmModalOpen = ref(false);

  // Form state
  const initialBalance = ref(0);
  const actualBalance = ref(0);
  const closeNotes = ref('');
  const cashPayments = ref(0);
  const cardPayments = ref(0);
  const digitalPayments = ref(0);
  const otherPayments = ref(0);
  const expenseAmount = ref(0);
  const expenseDescription = ref('');
  const expenseCategory = ref('');
  const useDenominationCounting = ref(false);
  const denominations = ref<Denominations>(createEmptyDenominations());
  const transactionToDelete = ref<Transaction | null>(null);
  const cutReport = ref<CutReport>({
    total_sales: 0,
    total_refunds: 0,
    total_tips: 0,
    total_expenses: 0,
    total_transactions: 0,
    net_cash_flow: 0
  });

  /**
   * Open session modal
   */
  const openOpenModal = () => {
    openModalOpen.value = true;
  };

  /**
   * Open close session modal
   */
  const openCloseModal = () => {
    closeModalOpen.value = true;
  };

  /**
   * Open expense modal
   */
  const openExpenseModal = () => {
    expenseModalOpen.value = true;
  };

  /**
   * Open cut modal
   */
  const openCutModal = () => {
    cutModalOpen.value = true;
  };

  /**
   * Open delete confirmation modal
   */
  const confirmDeleteTransaction = (transaction: Transaction) => {
    transactionToDelete.value = transaction;
    deleteConfirmModalOpen.value = true;
  };

  /**
   * Cancel delete
   */
  const cancelDelete = () => {
    deleteConfirmModalOpen.value = false;
    transactionToDelete.value = null;
  };

  /**
   * Close all modals and reset form state
   */
  const closeModals = () => {
    openModalOpen.value = false;
    closeModalOpen.value = false;
    cutModalOpen.value = false;
    expenseModalOpen.value = false;
    deleteConfirmModalOpen.value = false;
    
    // Reset form values
    initialBalance.value = 0;
    actualBalance.value = 0;
    closeNotes.value = '';
    cashPayments.value = 0;
    cardPayments.value = 0;
    digitalPayments.value = 0;
    otherPayments.value = 0;
    expenseAmount.value = 0;
    expenseDescription.value = '';
    expenseCategory.value = '';
    useDenominationCounting.value = false;
    denominations.value = createEmptyDenominations();
    transactionToDelete.value = null;
  };

  /**
   * Set cut report data
   */
  const setCutReport = (report: CutReport) => {
    cutReport.value = report;
  };

  /**
   * Set payment breakdown
   */
  const setPaymentBreakdown = (breakdown: {
    cash: number;
    card: number;
    digital: number;
    other: number;
  }) => {
    cashPayments.value = breakdown.cash;
    cardPayments.value = breakdown.card;
    digitalPayments.value = breakdown.digital;
    otherPayments.value = breakdown.other;
  };

  return {
    // Modal visibility
    openModalOpen,
    closeModalOpen,
    cutModalOpen,
    expenseModalOpen,
    deleteConfirmModalOpen,

    // Form state
    initialBalance,
    actualBalance,
    closeNotes,
    cashPayments,
    cardPayments,
    digitalPayments,
    otherPayments,
    expenseAmount,
    expenseDescription,
    expenseCategory,
    useDenominationCounting,
    denominations,
    transactionToDelete,
    cutReport,

    // Methods
    openOpenModal,
    openCloseModal,
    openExpenseModal,
    openCutModal,
    confirmDeleteTransaction,
    cancelDelete,
    closeModals,
    setCutReport,
    setPaymentBreakdown
  };
}
