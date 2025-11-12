import { ref, computed, onMounted, onUnmounted } from 'vue';
import cashRegisterService from '@/services/cashRegisterService';
import type { Transaction, CashRegisterSession } from '@/utils/cashRegisterHelpers';
import { calculateCurrentBalance, calculateSessionExpenses, calculateSessionDuration } from '@/utils/cashRegisterHelpers';

/**
 * Composable for cash register session management
 * Implements Single Responsibility Principle - only handles session and transaction state
 */
export function useCashRegisterSession() {
  // State
  const currentSession = ref<CashRegisterSession | null>(null);
  const transactions = ref<Transaction[]>([]);
  const isRefreshing = ref(false);
  const currentTime = ref(new Date());
  const lastCut = ref<any>(null);
  const lastCutLoading = ref(false);

  // Computed properties
  const currentBalance = computed(() => {
    if (!currentSession.value) return 0;
    return calculateCurrentBalance(currentSession.value.initial_balance || 0, transactions.value);
  });

  const sessionExpenses = computed(() => {
    return calculateSessionExpenses(transactions.value);
  });

  const sessionDuration = computed(() => {
    if (!currentSession.value?.opened_at) return '0h 0m';
    return calculateSessionDuration(currentSession.value.opened_at, currentTime.value);
  });

  /**
   * Load current active session
   */
  const loadCurrentSession = async () => {
    try {
      isRefreshing.value = true;
      const response = await cashRegisterService.getCurrentSession();
      currentSession.value = (response as any) || null;
      if (currentSession.value) {
        await loadTransactions();
        await loadLastCut();
      }
    } catch (error) {
      console.error('Error loading current session:', error);
    } finally {
      isRefreshing.value = false;
    }
  };

  /**
   * Load transactions for current session
   */
  const loadTransactions = async () => {
    if (!currentSession.value) return;

    try {
      const transactionsResponse = await cashRegisterService.getTransactions(currentSession.value.id);
      const transactionsData = Array.isArray(transactionsResponse) 
        ? transactionsResponse 
        : transactionsResponse.data || [];
      transactions.value = transactionsData;
    } catch (error) {
      console.error('Error loading transactions:', error);
      transactions.value = [];
    }
  };

  /**
   * Load last cut information
   */
  const loadLastCut = async () => {
    if (!currentSession.value) {
      lastCut.value = null;
      return;
    }

    try {
      lastCutLoading.value = true;
      const cutData = await cashRegisterService.getLastCut(currentSession.value.id);
      lastCut.value = cutData || null;
    } catch (error) {
      console.error('Error loading last cut:', error);
      lastCut.value = null;
    } finally {
      lastCutLoading.value = false;
    }
  };

  /**
   * Open a new session
   */
  const openSession = async (initialBalance: number): Promise<void> => {
    const response = await cashRegisterService.openSession(initialBalance);
    currentSession.value = response as any;
    await loadTransactions();
    await loadCurrentSession();
  };

  /**
   * Close current session
   */
  const closeSession = async (
    actualBalance: number, 
    notes?: string, 
    denominations?: any
  ): Promise<void> => {
    if (!currentSession.value) return;

    if (denominations) {
      await cashRegisterService.closeSessionWithDenominations(
        currentSession.value.id,
        actualBalance,
        notes,
        denominations
      );
    } else {
      await cashRegisterService.closeSession(
        currentSession.value.id,
        actualBalance,
        notes
      );
    }
    currentSession.value = null;
    transactions.value = [];
    await loadCurrentSession();
  };

  /**
   * Add expense to current session
   */
  const addExpense = async (amount: number, description: string, category?: string): Promise<void> => {
    if (!currentSession.value) {
      throw new Error('No active session');
    }

    await cashRegisterService.addExpense(currentSession.value.id, {
      amount,
      description,
      category
    });

    await loadCurrentSession();
  };

  /**
   * Perform a cut
   */
  const performCut = async (paymentBreakdown: {
    cash: number;
    card: number;
    digital: number;
    other: number;
  }): Promise<any> => {
    if (!currentSession.value) {
      throw new Error('No active session');
    }

    const result = await cashRegisterService.cutSession(currentSession.value.id, paymentBreakdown);
    await loadCurrentSession();
    return result.data || result;
  };

  /**
   * Delete a transaction
   */
  const deleteTransaction = async (transactionId: number): Promise<void> => {
    await cashRegisterService.deleteTransaction(transactionId);
    await loadCurrentSession();
  };

  /**
   * Set up timer for session duration updates
   */
  const setupTimer = () => {
    const timerInterval = setInterval(() => {
      currentTime.value = new Date();
    }, 60000); // Update every minute

    return timerInterval;
  };

  /**
   * Set up event listener for order payment completion
   */
  const setupEventListeners = () => {
    const handlePaymentCompleted = () => {
      loadCurrentSession();
    };

    window.addEventListener('orderPaymentCompleted', handlePaymentCompleted);

    return () => {
      window.removeEventListener('orderPaymentCompleted', handlePaymentCompleted);
    };
  };

  // Lifecycle
  let timerInterval: number | null = null;
  let cleanupEventListeners: (() => void) | null = null;

  onMounted(() => {
    loadCurrentSession();
    timerInterval = setupTimer();
    cleanupEventListeners = setupEventListeners();
  });

  onUnmounted(() => {
    if (timerInterval) {
      clearInterval(timerInterval);
    }
    if (cleanupEventListeners) {
      cleanupEventListeners();
    }
  });

  return {
    // State
    currentSession,
    transactions,
    isRefreshing,
    lastCut,
    lastCutLoading,

    // Computed
    currentBalance,
    sessionExpenses,
    sessionDuration,

    // Methods
    loadCurrentSession,
    loadTransactions,
    openSession,
    closeSession,
    addExpense,
    performCut,
    deleteTransaction
  };
}
