<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          {{ t('app.views.cashRegister.pastSessions') || 'Past Sessions' }}
        </h2>
        <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-2 sm:space-y-0">
          <input
            v-model="searchTerm"
            type="text"
            :placeholder="t('app.views.cashRegister.searchSessions') || 'Search sessions...'"
            class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <select
            v-model="statusFilter"
            class="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">{{ t('app.views.cashRegister.allStatuses') || 'All Statuses' }}</option>
            <option value="OPEN">{{ t('app.views.cashRegister.statusOpen') || 'Open' }}</option>
            <option value="CLOSED">{{ t('app.views.cashRegister.statusClosed') || 'Closed' }}</option>
          </select>
          <input
            v-model="startDate"
            type="date"
            class="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            v-model="endDate"
            type="date"
            class="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            @click="loadPastSessions"
            :disabled="isLoading"
            class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            <span v-if="isLoading" class="inline-block animate-spin mr-2">⟳</span>
            {{ t('app.actions.search') || 'Search' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="p-6 text-center">
      <p class="text-gray-500 dark:text-gray-400">
        {{ t('app.views.cashRegister.loading') || 'Loading past sessions...' }}
      </p>
    </div>

    <div v-else-if="pastSessions.length === 0" class="p-6 text-center">
      <p class="text-gray-500 dark:text-gray-400">
        {{ t('app.views.cashRegister.noPastSessions') || 'No past sessions found.' }}
      </p>
    </div>

    <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
      <div v-for="session in pastSessions" :key="session.id" class="px-4 sm:px-6 py-4">
        <div class="flex flex-col lg:flex-row lg:justify-between lg:items-center space-y-4 lg:space-y-0">
          <!-- Session Info -->
          <div class="flex-1">
            <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-2 sm:space-y-0">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {{ formatDate(session.created_at) }} - {{ formatDate(session.closed_at || session.created_at) }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.openedBy') || 'Opened by' }}: {{ session.opened_by_user?.full_name || session.opened_by_user?.email || 'Unknown' }}
                </p>
              </div>
              <div class="flex-shrink-0">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusBadgeClass(session.status)"
                >
                  {{ session.status }}
                </span>
              </div>
            </div>
          </div>

          <!-- Session Data and Actions -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:space-x-6 space-y-4 sm:space-y-0">
            <!-- Financial Data -->
            <div class="flex flex-wrap gap-4 sm:gap-6">
              <div class="text-center sm:text-right">
                <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.initialBalance') || 'Initial' }}
                </p>
                <p class="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">
                  ${{ session.initial_balance?.toFixed(2) || '0.00' }}
                </p>
              </div>
              <div v-if="session.final_balance" class="text-center sm:text-right">
                <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.finalBalance') || 'Final' }}
                </p>
                <p class="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">
                  ${{ session.final_balance?.toFixed(2) || '0.00' }}
                </p>
              </div>
              <div class="text-center sm:text-right">
                <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
                </p>
                <p class="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {{ session.transaction_count || 0 }}
                </p>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <button
                @click="viewSessionDetails(session.id)"
                class="w-full sm:w-auto px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                {{ t('app.actions.view') || 'View' }}
              </button>
              <button
                @click="viewSessionReport(session.id)"
                class="w-full sm:w-auto px-3 py-2 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                {{ t('app.views.cashRegister.report') || 'Report' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="pagination.total > pagination.limit" class="px-4 sm:px-6 py-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-3 sm:space-y-0">
        <div class="text-sm text-gray-500 dark:text-gray-400 text-center sm:text-left">
          {{ t('app.views.cashRegister.showing') || 'Showing' }} {{ pagination.offset + 1 }} {{ t('app.views.cashRegister.to') || 'to' }}
          {{ Math.min(pagination.offset + pagination.limit, pagination.total) }}
          {{ t('app.views.cashRegister.of') || 'of' }} {{ pagination.total }} {{ t('app.views.cashRegister.sessions') || 'sessions' }}
        </div>
        <div class="flex justify-center sm:justify-end space-x-2">
          <button
            @click="previousPage"
            :disabled="pagination.page <= 1"
            class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-white transition-colors"
          >
            {{ t('app.actions.previous') || 'Previous' }}
          </button>
          <button
            @click="nextPage"
            :disabled="pagination.page >= pagination.totalPages"
            class="px-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-white transition-colors"
          >
            {{ t('app.actions.next') || 'Next' }}
          </button>
        </div>
      </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { cashRegisterService } from '@/services/cashRegisterService'
import { useToast } from '@/composables/useToast'
import SessionDetailsModal from '@/components/SessionDetailsModal.vue'

const { t } = useI18n()
const toast = useToast()

const isLoading = ref(false)
const pastSessions = ref<any[]>([])
const searchTerm = ref('')
const statusFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const pagination = ref({
  page: 1,
  limit: 20,
  total: 0,
  totalPages: 0,
  offset: 0
})

// Modal state
const sessionDetailsModalOpen = ref(false)
const selectedSessionId = ref<number | null>(null)

const loadPastSessions = async () => {
  try {
    isLoading.value = true

    const filters: any = {
      page: pagination.value.page,
      limit: pagination.value.limit
    }

    if (searchTerm.value.trim()) {
      // For now, we'll filter client-side. In a real app, you'd want server-side search
    }

    if (statusFilter.value) {
      filters.status = statusFilter.value
    }

    if (startDate.value) {
      filters.start_date = startDate.value
    }

    if (endDate.value) {
      filters.end_date = endDate.value
    }

    const response = await cashRegisterService.getPastSessions(filters)

    // Handle both direct array response and paginated response
    if (Array.isArray(response)) {
      pastSessions.value = response
      pagination.value.total = response.length
      pagination.value.totalPages = Math.ceil(response.length / pagination.value.limit)
    } else if (response && response.data) {
      pastSessions.value = Array.isArray(response.data) ? response.data : response.data.sessions || []
      pagination.value.total = response.total || response.data?.total || pastSessions.value.length
      pagination.value.totalPages = response.totalPages || response.data?.totalPages || Math.ceil(pagination.value.total / pagination.value.limit)
    } else {
      pastSessions.value = []
      pagination.value.total = 0
      pagination.value.totalPages = 0
    }

    pagination.value.offset = (pagination.value.page - 1) * pagination.value.limit

  } catch (error: any) {
    console.error('Error loading past sessions:', error)
    toast.showToast(t('app.views.cashRegister.errorLoadingPastSessions') || 'Error loading past sessions', 'error')
    pastSessions.value = []
  } finally {
    isLoading.value = false
  }
}

const viewSessionDetails = (sessionId: number) => {
  selectedSessionId.value = sessionId
  sessionDetailsModalOpen.value = true
}

const closeSessionDetailsModal = () => {
  sessionDetailsModalOpen.value = false
  selectedSessionId.value = null
}

const viewSessionReport = async (sessionId: number) => {
  try {
    const report = await cashRegisterService.getSessionReport(sessionId)
    console.log('Session report:', report)
    toast.showToast(t('app.views.cashRegister.sessionReportGenerated') || 'Session report generated', 'success')
    // Here you could display the report in a modal or download it
  } catch (error: any) {
    console.error('Error generating session report:', error)
    toast.showToast(t('app.views.cashRegister.errorGeneratingReport') || 'Error generating session report', 'error')
  }
}

const previousPage = () => {
  if (pagination.value.page > 1) {
    pagination.value.page--
    loadPastSessions()
  }
}

const nextPage = () => {
  if (pagination.value.page < pagination.value.totalPages) {
    pagination.value.page++
    loadPastSessions()
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

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString() + ' ' + new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Watch for filter changes to reload data
watch([searchTerm, statusFilter, startDate, endDate], () => {
  pagination.value.page = 1
  loadPastSessions()
})

onMounted(() => {
  loadPastSessions()
})
</script>
