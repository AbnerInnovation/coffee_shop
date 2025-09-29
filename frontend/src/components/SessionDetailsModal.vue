<template>
  <div v-if="isVisible" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity" @click="closeModal">
        <div class="absolute inset-0 bg-gray-500 dark:bg-gray-900 opacity-75"></div>
      </div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <!-- Header -->
          <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
              {{ t('app.views.cashRegister.sessionDetails') || 'Session Details' }}
            </h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
            >
              <span class="sr-only">{{ t('app.actions.close') || 'Close' }}</span>
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Loading state -->
          <div v-if="isLoading" class="flex justify-center items-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <span class="ml-2 text-gray-600 dark:text-gray-400">
              {{ t('app.status.loading') || 'Loading...' }}
            </span>
          </div>

          <!-- Session details content -->
          <div v-else-if="session" class="space-y-6">
            <!-- Session Overview -->
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                {{ t('app.views.cashRegister.sessionOverview') || 'Session Overview' }}
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.openedBy') || 'Opened by' }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ session.opened_by_user?.full_name || session.opened_by_user?.email || 'Unknown' }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.status') || 'Status' }}
                  </p>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusBadgeClass(session.status)"
                  >
                    {{ session.status }}
                  </span>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.initialBalance') || 'Initial Balance' }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    ${{ session.initial_balance?.toFixed(2) || '0.00' }}
                  </p>
                </div>
                <div v-if="session.final_balance">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.finalBalance') || 'Final Balance' }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    ${{ session.final_balance?.toFixed(2) || '0.00' }}
                  </p>
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.startDate') || 'Start Date' }}
                  </p>
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ formatDate(session.created_at) }}
                  </p>
                </div>
                <div v-if="session.closed_at">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.endDate') || 'End Date' }}
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
                {{ t('app.views.cashRegister.paymentBreakdown') || 'Payment Breakdown' }}
              </h4>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.cashPayments') || 'Cash' }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    ${{ paymentBreakdown.cash?.toFixed(2) || '0.00' }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.cardPayments') || 'Card' }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    ${{ paymentBreakdown.card?.toFixed(2) || '0.00' }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.digitalPayments') || 'Digital' }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    ${{ paymentBreakdown.digital?.toFixed(2) || '0.00' }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.otherPayments') || 'Other' }}
                  </p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    ${{ paymentBreakdown.other?.toFixed(2) || '0.00' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Transactions -->
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <div class="flex justify-between items-center mb-4">
                <h4 class="text-md font-medium text-gray-900 dark:text-gray-100">
                  {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
                  <span class="text-sm text-gray-500 dark:text-gray-400 ml-2">
                    ({{ filteredTransactions.length }})
                  </span>
                </h4>

                <!-- Transaction Type Filter -->
                <select
                  v-model="transactionTypeFilter"
                  class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">{{ t('app.views.cashRegister.allTypes') || 'All Types' }}</option>
                  <option value="sale">{{ t('app.views.cashRegister.typeSale') || 'Sale' }}</option>
                  <option value="refund">{{ t('app.views.cashRegister.typeRefund') || 'Refund' }}</option>
                  <option value="tip">{{ t('app.views.cashRegister.typeTip') || 'Tip' }}</option>
                  <option value="adjustment">{{ t('app.views.cashRegister.typeAdjustment') || 'Adjustment' }}</option>
                </select>
              </div>

              <!-- Transaction Search -->
              <div class="mb-4">
                <input
                  v-model="transactionSearchTerm"
                  type="text"
                  :placeholder="t('app.views.cashRegister.searchTransactions') || 'Search transactions...'"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <!-- Transactions List -->
              <div v-if="filteredTransactions.length === 0" class="text-center py-4">
                <p class="text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.noTransactionsFound') || 'No transactions found.' }}
                </p>
              </div>
              <div v-else class="max-h-64 overflow-y-auto">
                <div v-for="transaction in paginatedTransactions" :key="transaction.id"
                     class="flex justify-between items-center py-2 px-3 bg-white dark:bg-gray-800 rounded-md mb-2">
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ transaction.description }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">
                      {{ formatDate(transaction.created_at) }}
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="text-sm font-semibold"
                       :class="transaction.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                      {{ transaction.amount >= 0 ? '+' : '' }}${{ transaction.amount?.toFixed(2) || '0.00' }}
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
                  {{ t('app.views.cashRegister.showing') || 'Showing' }}
                  {{ transactionPagination.offset + 1 }}
                  {{ t('app.views.cashRegister.to') || 'to' }}
                  {{ Math.min(transactionPagination.offset + transactionPagination.limit, filteredTransactions.length) }}
                  {{ t('app.views.cashRegister.of') || 'of' }}
                  {{ filteredTransactions.length }}
                  {{ t('app.views.cashRegister.transactions') || 'transactions' }}
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="previousTransactionPage"
                    :disabled="transactionPagination.page <= 1"
                    class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-white"
                  >
                    {{ t('app.actions.previous') || 'Previous' }}
                  </button>
                  <button
                    @click="nextTransactionPage"
                    :disabled="transactionPagination.page >= totalTransactionPages"
                    class="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-white"
                  >
                    {{ t('app.actions.next') || 'Next' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Session Summary -->
            <div v-if="sessionSummary" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 class="text-md font-medium text-gray-900 dark:text-gray-100 mb-3">
                {{ t('app.views.cashRegister.sessionSummary') || 'Session Summary' }}
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
                  </p>
                  <p class="text-xl font-bold text-green-600 dark:text-green-400">
                    ${{ sessionSummary.total_sales?.toFixed(2) || '0.00' }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
                  </p>
                  <p class="text-xl font-bold text-red-600 dark:text-red-400">
                    ${{ sessionSummary.total_refunds?.toFixed(2) || '0.00' }}
                  </p>
                </div>
                <div class="text-center">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
                  </p>
                  <p class="text-xl font-bold text-blue-600 dark:text-blue-400">
                    ${{ sessionSummary.net_cash_flow?.toFixed(2) || '0.00' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal footer -->
        <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            @click="closeModal"
            type="button"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            {{ t('app.actions.close') || 'Close' }}
          </button>
          <button
            v-if="session"
            @click="generateReport"
            type="button"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
          >
            {{ t('app.views.cashRegister.generateReport') || 'Generate Report' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { cashRegisterService } from '@/services/cashRegisterService'
import { useToast } from '@/composables/useToast'

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

  // Filter by search term
  if (transactionSearchTerm.value.trim()) {
    const searchTerm = transactionSearchTerm.value.toLowerCase()
    filtered = filtered.filter(transaction =>
      transaction.description.toLowerCase().includes(searchTerm)
    )
  }

  // Filter by transaction type
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

    // Load session details directly by ID
    const sessionResponse = await cashRegisterService.getSessionById(props.sessionId)
    session.value = sessionResponse || null

    if (!session.value) {
      toast.showToast(t('app.views.cashRegister.sessionNotFound') || 'Session not found', 'error')
      return
    }

    // Load transactions
    const transactionsResponse = await cashRegisterService.getTransactions(props.sessionId)
    transactions.value = Array.isArray(transactionsResponse) ? transactionsResponse : transactionsResponse.data || []

    // Load session report for summary and payment breakdown
    try {
      const reportResponse = await cashRegisterService.getSessionReport(props.sessionId)
      const reportData = reportResponse.data || reportResponse
      sessionSummary.value = reportData?.summary || null
      paymentBreakdown.value = reportData?.payment_breakdown || null
    } catch (reportError) {
      console.warn('Could not load session report:', reportError)
      // Continue without report data
    }

  } catch (error: any) {
    console.error('Error loading session details:', error)
    toast.showToast(t('app.views.cashRegister.errorLoadingSessionDetails') || 'Error loading session details', 'error')
  } finally {
    isLoading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

const generateReport = async () => {
  if (!props.sessionId) return

  try {
    const report = await cashRegisterService.getSessionReport(props.sessionId)
    const reportData = report.data || report
    console.log('Generated session report:', reportData)
    toast.showToast(t('app.views.cashRegister.sessionReportGenerated') || 'Session report generated', 'success')
    // Here you could display the report in a new modal or download it
  } catch (error: any) {
    console.error('Error generating session report:', error)
    toast.showToast(t('app.views.cashRegister.errorGeneratingReport') || 'Error generating session report', 'error')
  }
}

const previousTransactionPage = () => {
  if (transactionPagination.value.page > 1) {
    transactionPagination.value.page--
    transactionPagination.value.offset = (transactionPagination.value.page - 1) * transactionPagination.value.limit
  }
}

const nextTransactionPage = () => {
  if (transactionPagination.value.page < totalTransactionPages.value) {
    transactionPagination.value.page++
    transactionPagination.value.offset = (transactionPagination.value.page - 1) * transactionPagination.value.limit
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
      return t('app.views.cashRegister.typeSale') || 'Sale'
    case 'refund':
      return t('app.views.cashRegister.typeRefund') || 'Refund'
    case 'tip':
      return t('app.views.cashRegister.typeTip') || 'Tip'
    case 'adjustment':
      return t('app.views.cashRegister.typeAdjustment') || 'Adjustment'
    default:
      return type || 'Unknown'
  }
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

// Reset state when modal opens/closes
watch([() => props.isVisible, () => props.sessionId], () => {
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
  }
}, { immediate: true })
</script>
