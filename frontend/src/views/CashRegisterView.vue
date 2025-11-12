<template>
  <MainLayout>
    <PageHeader
      :title="t('app.views.cashRegister.title') || 'Cash Register'"
    />
    
    <!-- Tabs -->
    <div class="mb-4 overflow-x-auto">
      <nav class="flex space-x-4 sm:space-x-6 min-w-max border-b border-gray-200 dark:border-gray-700">
        <button @click="activeTab = 'current'"
          :class="activeTab === 'current' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'"
          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
          {{ t('app.views.cashRegister.currentSession') || 'Current Session' }}
        </button>
        <button @click="activeTab = 'reports'"
          :class="activeTab === 'reports' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'"
          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm">
          {{ t('app.views.cashRegister.reports') || 'Reports' }}
        </button>
      </nav>
    </div>

    <!-- Current Session Tab -->
    <div v-if="activeTab === 'current'">
      <div v-if="currentSession" class="mb-4 bg-white dark:bg-gray-800 rounded-lg shadow p-3 sm:p-4">
        <!-- Session Info Header -->
        <div class="mb-3">
          <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 text-center sm:text-left">
            <span class="font-medium">{{ t('app.views.cashRegister.sessionNumber') || 'Session' }} #{{ currentSession.session_number }}</span>
            <span class="mx-2">•</span>
            <span class="font-medium">{{ t('app.views.cashRegister.openedAt') || 'Opened' }}:</span>
            <span class="ml-2">{{ sessionDuration }}</span>
          </div>
        </div>

        <!-- Action Buttons - Grid layout for mobile, row for desktop -->
        <div class="grid grid-cols-2 sm:flex sm:flex-row gap-2 mb-3">
          <BaseButton @click="openExpenseModal" variant="warning" size="sm" class="w-full sm:w-auto">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
              </svg>
            </template>
            <span class="hidden sm:inline">{{ t('app.views.cashRegister.addExpense') || 'Add Expense' }}</span>
            <span class="sm:hidden">{{ t('app.views.cashRegister.expense') || 'Gasto' }}</span>
          </BaseButton>
          <BaseButton @click="openCutModal" variant="info" size="sm" class="w-full sm:w-auto">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
              </svg>
            </template>
            <span class="hidden sm:inline">{{ t('app.views.cashRegister.cut') || 'Cut' }}</span>
            <span class="sm:hidden">{{ t('app.views.cashRegister.cut') || 'Cortar' }}</span>
          </BaseButton>
          <BaseButton @click="openCloseModal" variant="danger" size="sm" class="w-full sm:w-auto col-span-2 sm:col-span-1">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </template>
            <span class="hidden sm:inline">{{ t('app.views.cashRegister.close') || 'Close Session' }}</span>
            <span class="sm:hidden">{{ t('app.views.cashRegister.closeSession') || 'Cerrar Sesión' }}</span>
          </BaseButton>
        </div>
        
        <!-- Stats Cards Component -->
        <SessionStatsCards
          :initial-balance="currentSession.initial_balance || 0"
          :current-balance="currentBalance"
          :transaction-count="transactions.length"
          :total-expenses="sessionExpenses"
          class="mb-3"
        />
        <LastCutDisplay :lastCut="lastCut" :isLoading="lastCutLoading" />
      </div>

      <!-- No Session Message -->
      <div v-else class="mb-8 text-center">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 sm:p-8">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 sm:h-16 sm:w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-base sm:text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
            {{ t('app.views.cashRegister.noActiveSession') || 'No Active Session' }}
          </h3>
          <p class="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-4">
            {{ t('app.views.cashRegister.openSessionToStart') || 'Open a session to start managing cash register operations.' }}
          </p>
          <BaseButton @click="openOpenModal" variant="primary" size="lg" full-width class="sm:w-auto">
            {{ t('app.views.cashRegister.openSession') || 'Open Session' }}
          </BaseButton>
        </div>
      </div>

      <!-- Transactions List Component -->
      <TransactionsList :transactions="transactions" />
    </div>

    <!-- Reports Tab -->
    <div v-if="activeTab === 'reports'">
      <ReportsView />
    </div>

    <!-- Modals -->
    <OpenSessionModal
      :is-open="openModalOpen"
      :initial-balance="initialBalance"
      @close="closeModals"
      @save="handleOpenSession"
    />

    
    <CloseSessionModal
      :is-open="closeModalOpen"
      :actual-balance="actualBalance"
      :notes="closeNotes"
      :use-denominations="useDenominationCounting"
      :denominations="denominations"
      @close="closeModals"
      @save="handleCloseSession"
    />

    
    <ExpenseModal
      :is-open="expenseModalOpen"
      :amount="expenseAmount"
      :description="expenseDescription"
      :category="expenseCategory"
      @close="closeModals"
      @save="handleAddExpense"
    />

    
    <CutModal
      :is-open="cutModalOpen"
      :report="cutReport"
      :cash="cashPayments"
      :card="cardPayments"
      :digital="digitalPayments"
      :other="otherPayments"
      @close="closeModals"
      @save="handlePerformCut"
    />
  </MainLayout>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import cashRegisterService from '@/services/cashRegisterService';
import { useToast } from '@/composables/useToast';
import { useCashRegisterSession } from '@/composables/useCashRegisterSession';
import { useCashRegisterModals } from '@/composables/useCashRegisterModals';
import {
  calculateCutReport,
  calculatePaymentBreakdown
} from '@/utils/cashRegisterHelpers';
import LastCutDisplay from '@/components/LastCutDisplay.vue';
import ReportsView from '@/components/ReportsView.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import SessionStatsCards from '@/components/cashRegister/SessionStatsCards.vue';
import TransactionsList from '@/components/cashRegister/TransactionsList.vue';
import OpenSessionModal from '@/components/cashRegister/OpenSessionModal.vue';
import CloseSessionModal from '@/components/cashRegister/CloseSessionModal.vue';
import ExpenseModal from '@/components/cashRegister/ExpenseModal.vue';
import CutModal from '@/components/cashRegister/CutModal.vue';

const { t } = useI18n();
const toast = useToast();

// Composables
const {
  currentSession,
  transactions,
  lastCut,
  lastCutLoading,
  currentBalance,
  sessionExpenses,
  sessionDuration,
  openSession: openSessionService,
  closeSession: closeSessionService,
  addExpense: addExpenseService,
  performCut: performCutService,
  deleteTransaction: deleteTransactionService
} = useCashRegisterSession();

const {
  openModalOpen,
  closeModalOpen,
  cutModalOpen,
  expenseModalOpen,
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
  cutReport,
  openOpenModal,
  openCloseModal,
  openExpenseModal,
  openCutModal: openCutModalBase,
  closeModals,
  setCutReport,
  setPaymentBreakdown
} = useCashRegisterModals();

const activeTab = ref('current');

// Open cut modal with pre-populated data
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
}

// Modal handlers
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
    toast.showToast(error.response?.data?.detail || 'Failed to open session', 'error');
  }
}

const handleCloseSession = async (data: { balance: number; notes: string; useDenominations: boolean; denominations: any }) => {
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
}

const handleAddExpense = async (data: { amount: number; description: string; category: string }) => {
  if (!data.amount || data.amount <= 0) {
    toast.showToast(t('app.views.cashRegister.expenseAmountRequired') || 'Expense amount is required', 'error');
    return;
  }

  if (!data.description || data.description.trim() === '') {
    toast.showToast(t('app.views.cashRegister.expenseDescriptionRequired') || 'Expense description is required', 'error');
    return;
  }

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
    toast.showToast(error.response?.data?.detail || t('app.views.cashRegister.expenseFailed') || 'Failed to add expense', 'error');
  }
}

const handlePerformCut = async (data: { cash: number; card: number; digital: number; other: number }) => {
  if (!currentSession.value) return;

  try {
    const resultData = await performCutService(data);
    
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
    toast.showToast(error.response?.data?.detail || t('app.views.cashRegister.cutFailed') || 'Failed to perform cut', 'error');
  }
}
</script>
