<template>
  <div v-if="isVisible" class="fixed inset-0 z-[10001] overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity" @click="closeModal">
        <div class="absolute inset-0 bg-gray-500 dark:bg-gray-900 opacity-75"></div>
      </div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full print-content">
        <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <!-- Header -->
          <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              {{ t('app.views.cashRegister.sessionDetails') }}
            </h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
            >
              <span class="sr-only">{{ t('app.actions.close') }}</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Loading state -->
          <div v-if="isLoading" class="flex justify-center items-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <span class="ml-2 text-gray-600 dark:text-gray-400">
              {{ t('app.status.loading') }}
            </span>
          </div>

          <!-- Session details content -->
          <div v-else-if="session" class="space-y-6">
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                {{ t('app.views.cashRegister.sessionOverview') }}
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.openedBy') }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ session.opened_by_user?.full_name || session.opened_by_user?.email || t('app.common.unknown') }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.status') }}
                  </p>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusBadgeClass(session.status)"
                  >
                    {{ translateStatus(session.status) }}
                  </span>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.initialBalance') }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ formatCurrency(session.initial_balance || 0) }}
                  </p>
                </div>
                <div v-if="session.expected_balance !== undefined">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.expectedBalance') }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ formatCurrency(session.expected_balance || 0) }}
                  </p>
                </div>
              </div>
              <!-- Cash reconciliation section for closed sessions -->
              <div v-if="session.status === 'CLOSED' && session.actual_balance !== null" class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.actualCash') }}
                  </p>
                  <p class="text-lg font-semibold text-blue-600 dark:text-blue-400">
                    {{ formatCurrency(session.actual_balance || 0) }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.actualCashDescription') }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.expectedCash') }}
                  </p>
                  <p class="text-lg font-semibold text-gray-700 dark:text-gray-300">
                    {{ formatCurrency(session.expected_balance || 0) }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.expectedCashDescription') }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.difference') }}
                  </p>
                  <p class="text-lg font-bold" :class="getDifferenceClass(session.actual_balance, session.expected_balance)">
                    {{ formatDifference(session.actual_balance, session.expected_balance) }}
                  </p>
                  <p class="text-xs" :class="getDifferenceTextClass(session.actual_balance, session.expected_balance)">
                    {{ getDifferenceLabel(session.actual_balance, session.expected_balance) }}
                  </p>
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.startDate') }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ formatDate(session.created_at) }}
                  </p>
                </div>
                <div v-if="session.closed_at">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.endDate') }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ formatDate(session.closed_at) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Payment Breakdown -->
            <div v-if="paymentBreakdown" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                {{ t('app.views.cashRegister.paymentBreakdown') }}
              </h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.cashPayments') }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {{ formatCurrency(paymentBreakdown.cash || 0) }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.cardPayments') }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {{ formatCurrency(paymentBreakdown.card || 0) }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.digitalPayments') }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {{ formatCurrency(paymentBreakdown.digital || 0) }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.otherPayments') }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {{ formatCurrency(paymentBreakdown.other || 0) }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Last Cut Information -->
            <CutDetails 
              :cut-data="lastCut" 
              :is-loading="lastCutLoading"
              :title="t('app.views.cashRegister.lastCut')"
            />

            <!-- Transactions -->
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div class="flex justify-between items-center mb-4">
                <h4 class="text-md font-medium text-gray-900 dark:text-gray-100">
                  {{ t('app.views.cashRegister.transactions') }}
                  <span class="text-sm text-gray-500 dark:text-gray-400 ml-2">
                    ({{ filteredTransactions.length }})
                  </span>
                </h4>

                <!-- Transaction Type Filter -->
                <select
                  v-model="transactionTypeFilter"
                  class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">{{ t('app.views.cashRegister.allTypes') }}</option>
                  <option value="sale">{{ t('app.views.cashRegister.typeSale') }}</option>
                  <option value="refund">{{ t('app.views.cashRegister.typeRefund') }}</option>
                  <option value="tip">{{ t('app.views.cashRegister.typeTip') }}</option>
                  <option value="adjustment">{{ t('app.views.cashRegister.typeAdjustment') }}</option>
                </select>
              </div>

              <!-- Transaction Search -->
              <div class="mb-4">
                <input
                  v-model="transactionSearchTerm"
                  type="text"
                  :placeholder="t('app.views.cashRegister.searchTransactions')"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <!-- Transactions List -->
              <div v-if="filteredTransactions.length === 0" class="text-center py-4">
                <p class="text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.noTransactionsFound') }}
                </p>
              </div>
              <div v-else class="max-h-64 overflow-y-auto">
                <div v-for="transaction in paginatedTransactions" :key="transaction.id"
                     class="flex justify-between items-center py-2 px-3 bg-white dark:bg-gray-800 rounded-md mb-2">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ translateDescription(transaction.description) }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {{ formatDate(transaction.created_at) }}
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="text-sm font-semibold"
                       :class="transaction.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                      {{ transaction.amount >= 0 ? '+' : '' }}{{ formatCurrency(Math.abs(transaction.amount || 0)) }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {{ getTransactionTypeLabel(transaction.transaction_type) }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Transaction Pagination -->
              <div v-if="totalTransactionPages > 1" class="flex justify-between items-center mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <div class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.showing') }}
                  {{ transactionPagination.offset + 1 }}
                  {{ t('app.views.cashRegister.to') }}
                  {{ Math.min(transactionPagination.offset + transactionPagination.limit, filteredTransactions.length) }}
                  {{ t('app.views.cashRegister.of') }}
                  {{ filteredTransactions.length }}
                  {{ t('app.views.cashRegister.transactions') }}
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="previousTransactionPage"
                    :disabled="transactionPagination.page <= 1"
                    class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-white"
                  >
                    {{ t('app.users.actions.previous') }}
                  </button>
                  <button
                    @click="nextTransactionPage"
                    :disabled="transactionPagination.page >= totalTransactionPages"
                    class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-white"
                  >
                    {{ t('app.users.actions.next') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Session Summary -->
            <div v-if="sessionSummary" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                {{ t('app.views.cashRegister.sessionSummary') }}
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.totalSales') }}
                  </p>
                  <p class="text-xl font-bold text-green-600 dark:text-green-400">
                    {{ formatCurrency(sessionSummary.total_sales || 0) }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.netCashFlow') }}
                  </p>
                  <p class="text-xl font-bold text-blue-600 dark:text-blue-400">
                    {{ formatCurrency(sessionSummary.net_cash_flow || 0) }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- No session state -->
          <div v-else class="flex justify-center items-center py-8">
            <p class="text-gray-600 dark:text-gray-400">
              {{ t('app.views.cashRegister.sessionNotFound') }}
            </p>
          </div>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse sm:gap-3 print:hidden">
          <button
            @click="closeModal"
            type="button"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:w-auto sm:text-sm"
          >
            {{ t('app.actions.close') }}
          </button>
          <button
            v-if="session"
            @click="printReport"
            type="button"
            class="mt-3 w-full inline-flex justify-center items-center gap-2 rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zm0 8H7v4h6v-4z" clip-rule="evenodd" />
            </svg>
            {{ t('app.actions.print') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { cashRegisterService } from '@/services/cashRegisterService'
import { useToast } from '@/composables/useToast'
import { formatCurrency } from '@/utils/priceHelpers'
import CutDetails from '@/components/cashRegister/CutDetails.vue'
import { formatDateTime as formatDate } from '@/utils/dateHelpers'

interface Props {
  isVisible: boolean
  sessionId?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

const { t } = useI18n()
const toast = useToast()

const isLoading = ref(false)
const session = ref<any>(null)
const transactions = ref<any[]>([])
const sessionSummary = ref<any>(null)
const paymentBreakdown = ref<any>(null)
const lastCut = ref<any>(null)
const lastCutLoading = ref(false)

// Transaction filtering and pagination
const transactionSearchTerm = ref('')
const transactionTypeFilter = ref('')
const transactionPagination = ref({
  page: 1,
  limit: 10,
  offset: 0
})

const filteredTransactions = computed(() => {
  let filtered = transactions.value

  if (transactionSearchTerm.value.trim()) {
    const searchTerm = transactionSearchTerm.value.toLowerCase()
    filtered = filtered.filter(transaction =>
      transaction.description.toLowerCase().includes(searchTerm)
    )
  }

  if (transactionTypeFilter.value) {
    filtered = filtered.filter(transaction =>
      transaction.transaction_type === transactionTypeFilter.value
    )
  }

  return filtered
})

const paginatedTransactions = computed(() => {
  const start = transactionPagination.value.offset
  const end = start + transactionPagination.value.limit
  return filteredTransactions.value.slice(start, end)
})

const totalTransactionPages = computed(() => {
  return Math.ceil(filteredTransactions.value.length / transactionPagination.value.limit)
})

const loadSessionDetails = async () => {
  if (!props.sessionId) return

  try {
    isLoading.value = true
    const sessionResponse = await cashRegisterService.getSessionById(props.sessionId)
    session.value = sessionResponse || null

    if (!session.value) {
      toast.showToast(t('app.views.cashRegister.sessionNotFound'), 'error')
      return
    }

    const transactionsResponse = await cashRegisterService.getTransactions(props.sessionId)
    transactions.value = Array.isArray(transactionsResponse)
      ? transactionsResponse
      : transactionsResponse.data || []

    try {
      const reportResponse = await cashRegisterService.getSessionReport(props.sessionId)
      const reportData = reportResponse.data || reportResponse
      sessionSummary.value = reportData?.summary || null
      paymentBreakdown.value = reportData?.payment_breakdown || null
    } catch (reportError) {
      console.warn('Could not load session report:', reportError)
    }

    loadLastCutForSession(props.sessionId)
  } catch (error: any) {
    console.error('Error loading session details:', error)
    toast.showToast(
      t('app.views.cashRegister.errorLoadingSessionDetails'),
      'error'
    )
  } finally {
    isLoading.value = false
  }
}

const loadLastCutForSession = async (sessionId: number) => {
  try {
    lastCutLoading.value = true
    const cutData = await cashRegisterService.getLastCut(sessionId)
    lastCut.value = cutData || null
  } catch (error) {
    console.error('Error loading last cut for session:', error)
    lastCut.value = null
  } finally {
    lastCutLoading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

const printReport = () => {
  if (!session.value) return
  
  // Use browser's print functionality
  window.print()
}

const previousTransactionPage = () => {
  if (transactionPagination.value.page > 1) {
    transactionPagination.value.page--
    transactionPagination.value.offset =
      (transactionPagination.value.page - 1) * transactionPagination.value.limit
  }
}

const nextTransactionPage = () => {
  if (transactionPagination.value.page < totalTransactionPages.value) {
    transactionPagination.value.page++
    transactionPagination.value.offset =
      (transactionPagination.value.page - 1) * transactionPagination.value.limit
  }
}

const translateStatus = (status: string) => {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return t('app.views.cashRegister.statusOpenBadge')
    case 'CLOSED':
      return t('app.views.cashRegister.statusClosedBadge')
    default:
      return status
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status?.toUpperCase()) {
    case 'OPEN':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    case 'CLOSED':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
    default:
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
  }
}

const getTransactionTypeLabel = (type: string) => {
  switch (type?.toLowerCase()) {
    case 'sale':
      return t('app.views.cashRegister.typeSale')
    case 'refund':
      return t('app.views.cashRegister.typeRefund')
    case 'tip':
      return t('app.views.cashRegister.typeTip')
    case 'adjustment':
      return t('app.views.cashRegister.typeAdjustment')
    default:
      return type || t('app.common.unknown')
  }
}

const translateDescription = (description: string) => {
  if (!description) return description
  
  // Traducir "Payment for order #X" a "Pago de orden #X"
  const paymentPattern = /^Payment for order #(\d+)$/i
  const match = description.match(paymentPattern)
  if (match) {
    return `Pago de orden #${match[1]}`
  }
  
  return description
}

// formatDate is now imported from @/utils/dateHelpers (as formatDateTime)
// formatCurrency is now imported from @/utils/priceHelpers

const formatDifference = (actual: number | null | undefined, expected: number | null | undefined) => {
  if (actual === null || actual === undefined || expected === null || expected === undefined) {
    return formatCurrency(0)
  }
  const diff = actual - expected
  return (diff >= 0 ? '+' : '') + formatCurrency(diff)
}

const getDifferenceClass = (actual: number | null | undefined, expected: number | null | undefined) => {
  if (actual === null || actual === undefined || expected === null || expected === undefined) {
    return 'text-gray-600 dark:text-gray-400'
  }
  const diff = actual - expected
  if (Math.abs(diff) < 0.01) return 'text-green-600 dark:text-green-400' // Exact match
  if (diff > 0) return 'text-blue-600 dark:text-blue-400' // Surplus
  return 'text-red-600 dark:text-red-400' // Shortage
}

const getDifferenceTextClass = (actual: number | null | undefined, expected: number | null | undefined) => {
  if (actual === null || actual === undefined || expected === null || expected === undefined) {
    return 'text-gray-500 dark:text-gray-400'
  }
  const diff = actual - expected
  if (Math.abs(diff) < 0.01) return 'text-green-600 dark:text-green-400'
  if (diff > 0) return 'text-blue-600 dark:text-blue-400'
  return 'text-red-600 dark:text-red-400'
}

const getDifferenceLabel = (actual: number | null | undefined, expected: number | null | undefined) => {
  if (actual === null || actual === undefined || expected === null || expected === undefined) {
    return t('app.common.na')
  }
  const diff = actual - expected
  if (Math.abs(diff) < 0.01) return t('app.views.cashRegister.exactMatch')
  if (diff > 0) return t('app.views.cashRegister.surplus')
  return t('app.views.cashRegister.shortage')
}

watch(
  [() => props.isVisible, () => props.sessionId],
  () => {
    if (props.isVisible && props.sessionId) {
      transactionSearchTerm.value = ''
      transactionTypeFilter.value = ''
      transactionPagination.value = {
        page: 1,
        limit: 10,
        offset: 0
      }
      loadSessionDetails()
    } else {
      session.value = null
      transactions.value = []
      sessionSummary.value = null
      paymentBreakdown.value = null
      lastCut.value = null
    }
  },
  { immediate: true }
)
</script>

<style>
@media print {
  @page {
    margin: 0.5cm;
  }
  
  /* Simple approach - hide everything, show only print-content */
  body * {
    visibility: hidden;
  }
  
  .print-content,
  .print-content * {
    visibility: visible;
  }
  
  .fixed.inset-0.z-50,
  .flex.items-center {
    position: static !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  
  .print-content {
    position: static !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Hide buttons, inputs, and icons */
  button, input, select, textarea, svg {
    display: none !important;
  }
  
  /* Force black and white for print */
  * {
    background-color: white !important;
    color: black !important;
    border-color: #000 !important;
    box-shadow: none !important;
  }
  
  /* Colored sections get borders */
  .bg-green-50, .bg-red-50, .bg-blue-50, .bg-purple-50,
  .dark\:bg-green-900\/30, .dark\:bg-red-900\/30, .dark\:bg-blue-900\/30, .dark\:bg-purple-900\/30 {
    background-color: white !important;
    border: 2px solid black !important;
  }
  
  /* Bold headings */
  h1, h2, h3, h4, h5, h6 {
    font-weight: bold !important;
  }
  
  /* Compact spacing */
  .p-6, .p-4, .px-4, .px-6, .pt-5, .pb-4 {
    padding: 0.25rem !important;
  }
  
  .mb-4, .mb-6 {
    margin-bottom: 0.25rem !important;
  }
  
  /* Remove rounded corners */
  .rounded-lg {
    border-radius: 0 !important;
  }
}
</style>
