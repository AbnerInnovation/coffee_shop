<template>
  <div class="space-y-6">
    <!-- Report Type Selector -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6">
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            {{ t('app.views.cashRegister.reportType') || 'Report Type' }}
          </label>
          <select v-model="reportType" 
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500">
            <option value="daily">{{ t('app.views.cashRegister.dailySummaries') || 'Daily Summaries' }}</option>
            <option value="weekly">{{ t('app.views.cashRegister.weeklySummary') || 'Weekly Summary' }}</option>
          </select>
        </div>
        
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
            {{ t('app.views.cashRegister.dateRange') || 'Date Range' }}
          </label>
          <div class="flex gap-2">
            <BaseButton 
              @click="setDateRange('today')" 
              :variant="dateRangeType === 'today' ? 'primary' : 'secondary'"
              size="sm"
              class="flex-1">
              {{ t('app.views.cashRegister.today') || 'Today' }}
            </BaseButton>
            <BaseButton 
              @click="setDateRange('week')" 
              :variant="dateRangeType === 'week' ? 'primary' : 'secondary'"
              size="sm"
              class="flex-1">
              {{ t('app.views.cashRegister.thisWeek') || 'Week' }}
            </BaseButton>
            <BaseButton 
              @click="setDateRange('month')" 
              :variant="dateRangeType === 'month' ? 'primary' : 'secondary'"
              size="sm"
              class="flex-1">
              {{ t('app.views.cashRegister.thisMonth') || 'Month' }}
            </BaseButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-gray-600 dark:text-gray-400">{{ t('app.common.loading') || 'Loading...' }}</p>
    </div>

    <!-- Daily Summaries View -->
    <div v-else-if="reportType === 'daily' && dailyReports.length > 0" class="space-y-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
        {{ t('app.views.cashRegister.dailySummaries') || 'Daily Summaries' }}
      </h3>
      
      <div v-for="(report, index) in dailyReports" :key="index" 
        class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-3 mb-4">
          <div class="flex-1">
            <h4 class="text-md font-medium text-gray-900 dark:text-gray-100">
              {{ t('app.views.cashRegister.sessionReport') || 'Session Report' }} #{{ report.session_number }}
            </h4>
            <div class="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 mt-1">
              <p class="text-xs text-gray-500 dark:text-gray-400">
                <span class="font-medium">{{ t('app.views.cashRegister.opened') || 'Opened' }}:</span> {{ formatDateTime(report.opened_at) }}
              </p>
              <p v-if="report.closed_at" class="text-xs text-gray-500 dark:text-gray-400">
                <span class="font-medium">{{ t('app.views.cashRegister.closed') || 'Closed' }}:</span> {{ formatDateTime(report.closed_at) }}
              </p>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ report.total_transactions }} {{ t('app.views.cashRegister.transactions') || 'transactions' }}
            </p>
          </div>
          <BaseButton 
            @click="viewSessionDetails(report.session_id)"
            variant="info"
            size="sm"
            full-width
            class="sm:w-auto">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
              </svg>
            </template>
            {{ t('app.views.cashRegister.details') || 'Details' }}
          </BaseButton>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-green-50 dark:bg-green-900/30 p-3 rounded-lg">
            <p class="text-xs text-green-800 dark:text-green-200 mb-1">
              {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
            </p>
            <p class="text-lg font-bold text-green-600 dark:text-green-400">
              {{ formatCurrency(report.total_sales || 0) }}
            </p>
          </div>
          
          <div class="bg-red-50 dark:bg-red-900/30 p-3 rounded-lg">
            <p class="text-xs text-red-800 dark:text-red-200 mb-1">
              {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
            </p>
            <p class="text-lg font-bold text-red-600 dark:text-red-400">
              {{ formatCurrency(report.total_refunds || 0) }}
            </p>
          </div>
          
          <div class="bg-purple-50 dark:bg-purple-900/30 p-3 rounded-lg">
            <p class="text-xs text-purple-800 dark:text-purple-200 mb-1">
              {{ t('app.views.cashRegister.totalTips') || 'Total Tips' }}
            </p>
            <p class="text-lg font-bold text-purple-600 dark:text-purple-400">
              {{ formatCurrency(report.total_tips || 0) }}
            </p>
          </div>
          
          <div class="bg-amber-50 dark:bg-amber-900/30 p-3 rounded-lg">
            <p class="text-xs text-amber-800 dark:text-amber-200 mb-1">
              {{ t('app.views.cashRegister.totalExpenses') || 'Total Expenses' }}
            </p>
            <p class="text-lg font-bold text-amber-600 dark:text-amber-400">
              {{ formatCurrency(report.total_expenses || 0) }}
            </p>
          </div>
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
            </span>
            <span class="text-xl font-bold text-indigo-600 dark:text-indigo-400">
              {{ formatCurrency(report.net_cash_flow || 0) }}
            </span>
          </div>
          
          <div class="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
            <div class="text-sm">
              <span class="text-gray-600 dark:text-gray-400">Cash:</span>
              <span class="ml-1 font-medium">{{ formatCurrency(report.payment_breakdown?.cash || 0) }}</span>
            </div>
            <div class="text-sm">
              <span class="text-gray-600 dark:text-gray-400">Card:</span>
              <span class="ml-1 font-medium">{{ formatCurrency(report.payment_breakdown?.card || 0) }}</span>
            </div>
            <div class="text-sm">
              <span class="text-gray-600 dark:text-gray-400">Digital:</span>
              <span class="ml-1 font-medium">{{ formatCurrency(report.payment_breakdown?.digital || 0) }}</span>
            </div>
            <div class="text-sm">
              <span class="text-gray-600 dark:text-gray-400">Other:</span>
              <span class="ml-1 font-medium">{{ formatCurrency(report.payment_breakdown?.other || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Weekly Summary View -->
    <div v-else-if="reportType === 'weekly' && weeklySummary" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.weeklySummary') || 'Weekly Summary' }}
      </h3>
      
      <div class="mb-6">
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ formatDate(weeklySummary.start_date) }} - {{ formatDate(weeklySummary.end_date) }}
        </p>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          {{ t('app.views.cashRegister.totalSessions') || 'Total Sessions' }}: 
          <span class="font-medium">{{ weeklySummary.total_sessions }}</span>
        </p>
      </div>
      
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <div class="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg">
          <p class="text-xs text-green-800 dark:text-green-200 mb-1">
            {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
          </p>
          <p class="text-xl font-bold text-green-600 dark:text-green-400">
            {{ formatCurrency(weeklySummary.total_sales || 0) }}
          </p>
        </div>
        
        <div class="bg-red-50 dark:bg-red-900/30 p-4 rounded-lg">
          <p class="text-xs text-red-800 dark:text-red-200 mb-1">
            {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
          </p>
          <p class="text-xl font-bold text-red-600 dark:text-red-400">
            {{ formatCurrency(weeklySummary.total_refunds || 0) }}
          </p>
        </div>
        
        <div class="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg">
          <p class="text-xs text-purple-800 dark:text-purple-200 mb-1">
            {{ t('app.views.cashRegister.totalTips') || 'Total Tips' }}
          </p>
          <p class="text-xl font-bold text-purple-600 dark:text-purple-400">
            {{ formatCurrency(weeklySummary.total_tips || 0) }}
          </p>
        </div>
        
        <div class="bg-amber-50 dark:bg-amber-900/30 p-4 rounded-lg">
          <p class="text-xs text-amber-800 dark:text-amber-200 mb-1">
            {{ t('app.views.cashRegister.totalExpenses') || 'Total Expenses' }}
          </p>
          <p class="text-xl font-bold text-amber-600 dark:text-amber-400">
            {{ formatCurrency(weeklySummary.total_expenses || 0) }}
          </p>
        </div>
        
        <div class="bg-indigo-50 dark:bg-indigo-900/30 p-4 rounded-lg">
          <p class="text-xs text-indigo-800 dark:text-indigo-200 mb-1">
            {{ t('app.views.cashRegister.avgSessionValue') || 'Avg Session' }}
          </p>
          <p class="text-xl font-bold text-indigo-600 dark:text-indigo-400">
            {{ formatCurrency(weeklySummary.average_session_value || 0) }}
          </p>
        </div>
      </div>
      
      <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <span class="text-lg font-medium text-gray-700 dark:text-gray-300">
            {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
          </span>
          <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
            {{ formatCurrency(weeklySummary.net_cash_flow || 0) }}
          </span>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Cash Payments</p>
            <p class="text-lg font-semibold">{{ formatCurrency(weeklySummary.payment_breakdown?.cash || 0) }}</p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Card Payments</p>
            <p class="text-lg font-semibold">{{ formatCurrency(weeklySummary.payment_breakdown?.card || 0) }}</p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Digital Payments</p>
            <p class="text-lg font-semibold">{{ formatCurrency(weeklySummary.payment_breakdown?.digital || 0) }}</p>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
            <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Other Payments</p>
            <p class="text-lg font-semibold">{{ formatCurrency(weeklySummary.payment_breakdown?.other || 0) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- No Data State -->
    <div v-else-if="!loading" class="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-gray-600 dark:text-gray-400">
        {{ t('app.views.cashRegister.noReportsFound') || 'No reports found for the selected period.' }}
      </p>
    </div>
  </div>

  <!-- Session Details Modal -->
  <SessionDetailsModal
    :is-visible="sessionDetailsModalOpen"
    :session-id="selectedSessionId || undefined"
    @close="closeSessionDetailsModal"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { cashRegisterService } from '@/services/cashRegisterService'
import { useToast } from '@/composables/useToast'
import { formatCurrency } from '@/utils/priceHelpers'
import SessionDetailsModal from '@/components/SessionDetailsModal.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const { t } = useI18n()
const toast = useToast()

const reportType = ref('daily')
const startDate = ref('')
const endDate = ref('')
const dateRangeType = ref('week')
const loading = ref(false)
const dailyReports = ref<any[]>([])
const weeklySummary = ref<any>(null)
const sessionDetailsModalOpen = ref(false)
const selectedSessionId = ref<number | null>(null)

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch (error) {
    return 'Invalid date'
  }
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (error) {
    return 'Invalid date'
  }
}


const loadReports = async () => {
  loading.value = true
  try {
    if (reportType.value === 'daily') {
      const response = await cashRegisterService.getDailySummaries(startDate.value, endDate.value)
      dailyReports.value = Array.isArray(response) ? response : response.data || []
      weeklySummary.value = null
    } else if (reportType.value === 'weekly') {
      const response = await cashRegisterService.getWeeklySummary(startDate.value, endDate.value)
      weeklySummary.value = response.data || response
      dailyReports.value = []
    }
  } catch (error: any) {
    console.error('Error loading reports:', error)
    toast.showToast(error.response?.data?.detail || 'Failed to load reports', 'error')
  } finally {
    loading.value = false
  }
}

const setDateRange = (range: 'today' | 'week' | 'month') => {
  dateRangeType.value = range
  const today = new Date()
  endDate.value = today.toISOString().split('T')[0]
  
  switch (range) {
    case 'today':
      startDate.value = today.toISOString().split('T')[0]
      break
    case 'week':
      const lastWeek = new Date(today)
      lastWeek.setDate(today.getDate() - 7)
      startDate.value = lastWeek.toISOString().split('T')[0]
      break
    case 'month':
      const lastMonth = new Date(today)
      lastMonth.setMonth(today.getMonth() - 1)
      startDate.value = lastMonth.toISOString().split('T')[0]
      break
  }
  
  loadReports()
}

const viewSessionDetails = (sessionId: number) => {
  selectedSessionId.value = sessionId
  sessionDetailsModalOpen.value = true
}

const closeSessionDetailsModal = () => {
  sessionDetailsModalOpen.value = false
  selectedSessionId.value = null
}

onMounted(() => {
  // Set default to last week
  setDateRange('week')
})
</script>
