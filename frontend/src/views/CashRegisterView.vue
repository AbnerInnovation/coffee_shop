<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
          {{ t('app.views.cashRegister.title') || 'Cash Register' }}
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('app.views.cashRegister.subtitle') || 'Manage cash register sessions and transactions' }}
        </p>
      </div>

      <!-- Current Session Status -->
      <div v-if="currentSession" class="mb-8 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.currentSession') || 'Current Session' }}
          </h2>
          <div class="flex space-x-2">
            <button
              @click="openCutModal"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {{ t('app.views.cashRegister.cut') || 'Cut' }}
            </button>
            <button
              @click="openCloseModal"
              class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              {{ t('app.views.cashRegister.close') || 'Close' }}
            </button>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-green-50 dark:bg-green-900 p-4 rounded-md">
            <h3 class="text-lg font-medium text-green-800 dark:text-green-200">
              {{ t('app.views.cashRegister.initialBalance') || 'Initial Balance' }}
            </h3>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">
              ${{ currentSession.initial_balance?.toFixed(2) || '0.00' }}
            </p>
          </div>
          <div class="bg-blue-50 dark:bg-blue-900 p-4 rounded-md">
            <h3 class="text-lg font-medium text-blue-800 dark:text-blue-200">
              {{ t('app.views.cashRegister.currentBalance') || 'Current Balance' }}
            </h3>
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              ${{ currentBalance.toFixed(2) }}
            </p>
          </div>
          <div class="bg-purple-50 dark:bg-purple-900 p-4 rounded-md">
            <h3 class="text-lg font-medium text-purple-800 dark:text-purple-200">
              {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
            </h3>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {{ transactions.length }}
            </p>
          </div>
        </div>
      </div>

      <!-- No Session Message -->
      <div v-else class="mb-8 text-center">
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          {{ t('app.views.cashRegister.noSession') || 'No cash register session is currently open.' }}
        </p>
        <button
          @click="openOpenModal"
          class="px-6 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          {{ t('app.views.cashRegister.openSession') || 'Open Session' }}
        </button>
      </div>

      <!-- Transactions List -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
          </h2>
        </div>
        <div v-if="transactions.length === 0" class="p-6 text-center">
          <p class="text-gray-500 dark:text-gray-400">
            {{ t('app.views.cashRegister.noTransactions') || 'No transactions yet.' }}
          </p>
        </div>
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div v-for="transaction in transactions" :key="transaction.id" class="px-6 py-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ transaction.description }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(transaction.created_at) }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-lg font-semibold" :class="transaction.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
                  {{ transaction.amount >= 0 ? '+' : '' }}${{ transaction.amount?.toFixed(2) || '0.00' }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ transaction.transaction_type }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Open Session Modal -->
      <div v-if="openModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
        <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {{ t('app.views.cashRegister.openSession') || 'Open Session' }}
          </h3>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.initialBalance') || 'Initial Balance' }}
          </label>
          <input
            v-model="initialBalance"
            type="number"
            step="0.01"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-sm"
              @click="closeModals"
            >
              {{ t('app.actions.cancel') || 'Cancel' }}
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-md bg-indigo-600 text-white text-sm"
              @click="openSession"
            >
              {{ t('app.actions.save') || 'Save' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Close Session Modal -->
      <div v-if="closeModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
        <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {{ t('app.views.cashRegister.closeSession') || 'Close Session' }}
          </h3>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.actualBalance') || 'Actual Balance' }}
          </label>
          <input
            v-model="actualBalance"
            type="number"
            step="0.01"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mt-4 mb-1">
            {{ t('app.views.cashRegister.notes') || 'Notes' }}
          </label>
          <textarea
            v-model="closeNotes"
            rows="3"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          ></textarea>
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-sm"
              @click="closeModals"
            >
              {{ t('app.actions.cancel') || 'Cancel' }}
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-md bg-red-600 text-white text-sm"
              @click="closeSession"
            >
              {{ t('app.actions.save') || 'Save' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Cut Modal -->
      <div v-if="cutModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
        <div class="w-full max-w-lg rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {{ t('app.views.cashRegister.cutSession') || 'Cut Session' }}
          </h3>
          <div class="space-y-4">
            <div>
              <h4 class="font-medium text-gray-900 dark:text-gray-100">
                {{ t('app.views.cashRegister.summary') || 'Summary' }}
              </h4>
              <div class="mt-2 space-y-2">
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">
                    {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
                  </span>
                  <span class="font-medium">${{ cutReport.total_sales?.toFixed(2) || '0.00' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">
                    {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
                  </span>
                  <span class="font-medium">${{ cutReport.total_refunds?.toFixed(2) || '0.00' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600 dark:text-gray-400">
                    {{ t('app.views.cashRegister.totalTips') || 'Total Tips' }}
                  </span>
                  <span class="font-medium">${{ cutReport.total_tips?.toFixed(2) || '0.00' }}</span>
                </div>
                <div class="flex justify-between font-bold">
                  <span class="text-gray-900 dark:text-gray-100">
                    {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
                  </span>
                  <span>${{ cutReport.net_cash_flow?.toFixed(2) || '0.00' }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-sm"
              @click="closeModals"
            >
              {{ t('app.actions.cancel') || 'Cancel' }}
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-md bg-blue-600 text-white text-sm"
              @click="performCut"
            >
              {{ t('app.actions.save') || 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { cashRegisterService } from '@/services/cashRegisterService'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const toast = useToast()

const currentSession = ref<any>(null)
const transactions = ref<any[]>([])
const currentBalance = ref(0)
const openModalOpen = ref(false)
const closeModalOpen = ref(false)
const cutModalOpen = ref(false)
const initialBalance = ref(0)
const actualBalance = ref(0)
const closeNotes = ref('')
const cutReport = ref({
  total_sales: 0,
  total_refunds: 0,
  total_tips: 0,
  net_cash_flow: 0
})

const openOpenModal = () => {
  openModalOpen.value = true
}

const openCloseModal = () => {
  closeModalOpen.value = true
}

const openCutModal = () => {
  cutModalOpen.value = true
}

const closeModals = () => {
  openModalOpen.value = false
  closeModalOpen.value = false
  cutModalOpen.value = false
  initialBalance.value = 0
  actualBalance.value = 0
  closeNotes.value = ''
}

const openSession = async () => {
  if (!initialBalance.value) {
    toast.showToast(t('app.views.cashRegister.initialBalanceRequired') || 'Initial balance is required', 'error')
    return
  }

  try {
    const session = await cashRegisterService.openSession(Number(initialBalance.value))
    currentSession.value = session
    closeModals()
    loadTransactions()
    toast.showToast(t('app.views.cashRegister.sessionOpened') || 'Session opened successfully', 'success')
  } catch (error: any) {
    console.error('Error opening session:', error)
    toast.showToast(error.response?.data?.detail || 'Failed to open session', 'error')
  }
}

const closeSession = async () => {
  if (!actualBalance.value) {
    toast.showToast(t('app.views.cashRegister.finalBalanceRequired') || 'Final balance is required', 'error')
    return
  }

  try {
    const session = await cashRegisterService.closeSession(
      currentSession.value.id,
      Number(actualBalance.value)
    )
    currentSession.value = session
    closeModals()
    toast.showToast(t('app.views.cashRegister.sessionClosed') || 'Session closed successfully', 'success')
    currentSession.value = null
    transactions.value = []
    currentBalance.value = 0
  } catch (error: any) {
    console.error('Error closing session:', error)
    toast.showToast(error.response?.data?.detail || 'Failed to close session', 'error')
  }
}

const performCut = async () => {
  if (!currentSession.value) return

  try {
    const result = await cashRegisterService.cutSession(currentSession.value.id)
    toast.showToast(t('app.views.cashRegister.cutSuccessful') || 'Cut performed successfully', 'success')
    loadCurrentSession()
    closeModals()
  } catch (error: any) {
    console.error('Error performing cut:', error)
    toast.showToast(error.response?.data?.detail || t('app.views.cashRegister.cutFailed') || 'Failed to perform cut', 'error')
  }
}

const loadCurrentSession = async () => {
  try {
    console.log('Loading current session...')
    const session = await cashRegisterService.getCurrentSession()
    console.log('Current session response:', session)
    currentSession.value = session || null
    console.log('Current session state:', currentSession.value)
    if (currentSession.value) {
      console.log('Loading transactions for session:', currentSession.value.id)
      loadTransactions()
    } else {
      console.log('No current session found')
    }
  } catch (error) {
    console.error('Error loading current session:', error)
  }
}

const loadTransactions = async () => {
  if (!currentSession.value) return

  try {
    // Get transactions for current session
    const sessionData = await cashRegisterService.getSessionReport(currentSession.value.id)
    if (sessionData) {
      transactions.value = sessionData.transactions || []
      currentBalance.value = (currentSession.value.initial_balance || 0) + transactions.value.reduce((sum, t) => sum + (t.amount || 0), 0)
    }
  } catch (error) {
    console.error('Error loading transactions:', error)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadCurrentSession()
  // Refresh session state every 30 seconds to catch sessions opened in other tabs
  const refreshInterval = setInterval(() => {
    loadCurrentSession()
  }, 30000)

  // Refresh session state when tab gets focus (in case session was opened in another tab)
  const handleFocus = () => {
    loadCurrentSession()
  }
  window.addEventListener('focus', handleFocus)

  // Store interval and event listener for cleanup
  onUnmounted(() => {
    clearInterval(refreshInterval)
    window.removeEventListener('focus', handleFocus)
  })
})
</script>
