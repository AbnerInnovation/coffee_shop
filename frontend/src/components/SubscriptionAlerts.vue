<template>
  <div>
    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 mb-4">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'unread'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'unread'
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ t('app.subscription.alerts.unread') }}
          <span v-if="unreadCount > 0" class="ml-2 py-0.5 px-2 rounded-full text-xs bg-indigo-100 text-indigo-600 dark:bg-indigo-900 dark:text-indigo-300">
            {{ unreadCount }}
          </span>
        </button>
        <button
          @click="activeTab = 'read'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm',
            activeTab === 'read'
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ t('app.subscription.alerts.read') }}
        </button>
      </nav>
    </div>

    <!-- Alerts List -->
    <div v-if="filteredAlerts.length > 0" class="space-y-2">
      <div
        v-for="alert in filteredAlerts"
        :key="alert.id"
        :class="[
          'p-4 rounded-lg border-l-4 flex items-start justify-between',
          getAlertClass(alert.alert_type)
        ]"
      >
        <div class="flex items-start flex-1">
          <component 
            :is="getAlertIcon(alert.alert_type)" 
            class="w-5 h-5 mr-3 flex-shrink-0 mt-0.5"
          />
          <div class="flex-1">
            <h4 class="text-sm font-semibold mb-1">
              {{ alert.title }}
            </h4>
            <p class="text-sm">
              {{ alert.message }}
            </p>
            <p class="text-xs mt-1 opacity-75">
              {{ formatDate(alert.created_at) }}
            </p>
          </div>
        </div>

        <button
          v-if="!alert.is_read"
          @click="markAsRead(alert.id)"
          class="ml-4 text-sm hover:underline flex-shrink-0"
        >
          {{ t('app.common.mark_read') }}
        </button>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <BellAlertIcon class="mx-auto h-12 w-12 text-gray-400" />
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
        {{ activeTab === 'unread' ? t('app.subscription.alerts.no_unread') : t('app.subscription.alerts.no_read') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { 
  ExclamationTriangleIcon, 
  ClockIcon, 
  XCircleIcon, 
  CheckCircleIcon,
  BellAlertIcon
} from '@heroicons/vue/24/outline'
import { alertService, type SubscriptionAlert } from '@/services/alertService'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { showSuccess } = useToast()

interface Props {
  unreadOnly?: boolean
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  unreadOnly: false,
  autoRefresh: false,
  refreshInterval: 60000 // 1 minute
})

const emit = defineEmits(['update:count'])

const alerts = ref<SubscriptionAlert[]>([])
const loading = ref(false)
const activeTab = ref<'unread' | 'read'>('unread')
let refreshTimer: number | null = null

const unreadCount = computed(() => {
  return alerts.value.filter(a => !a.is_read).length
})

const filteredAlerts = computed(() => {
  if (activeTab.value === 'unread') {
    return alerts.value.filter(a => !a.is_read)
  } else {
    return alerts.value.filter(a => a.is_read)
  }
})

const loadAlerts = async () => {
  loading.value = true
  try {
    // Always load all alerts to support both tabs
    alerts.value = await alertService.getAlerts(false)
    emit('update:count', unreadCount.value)
  } catch (error) {
    console.error('Error loading alerts:', error)
  } finally {
    loading.value = false
  }
}

const markAsRead = async (alertId: number) => {
  try {
    await alertService.markAsRead([alertId])
    
    // Update local state
    const alert = alerts.value.find(a => a.id === alertId)
    if (alert) {
      alert.is_read = true
      alert.read_at = new Date().toISOString()
    }
    
    emit('update:count', unreadCount.value)
    showSuccess(t('app.subscription.alerts.marked_read'))
  } catch (error) {
    console.error('Error marking alert as read:', error)
  }
}

const getAlertClass = (type: string) => {
  const classes: Record<string, string> = {
    expiring_soon: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-400 text-yellow-800 dark:text-yellow-300',
    grace_period: 'bg-orange-50 dark:bg-orange-900/20 border-orange-400 text-orange-800 dark:text-orange-300',
    suspended: 'bg-red-50 dark:bg-red-900/20 border-red-500 text-red-800 dark:text-red-300',
    payment_approved: 'bg-green-50 dark:bg-green-900/20 border-green-500 text-green-800 dark:text-green-300',
    payment_rejected: 'bg-red-50 dark:bg-red-900/20 border-red-500 text-red-800 dark:text-red-300'
  }
  return classes[type] || 'bg-blue-50 dark:bg-blue-900/20 border-blue-400 text-blue-800 dark:text-blue-300'
}

const getAlertIcon = (type: string) => {
  const icons: Record<string, any> = {
    expiring_soon: ClockIcon,
    grace_period: ExclamationTriangleIcon,
    suspended: XCircleIcon,
    payment_approved: CheckCircleIcon,
    payment_rejected: XCircleIcon
  }
  return icons[type] || BellAlertIcon
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return t('app.common.just_now')
  if (diffMins < 60) return t('app.common.minutes_ago', { count: diffMins })
  if (diffHours < 24) return t('app.common.hours_ago', { count: diffHours })
  if (diffDays < 7) return t('app.common.days_ago', { count: diffDays })
  
  return date.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const startAutoRefresh = () => {
  if (props.autoRefresh && !refreshTimer) {
    refreshTimer = window.setInterval(loadAlerts, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  loadAlerts()
  startAutoRefresh()
})

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopAutoRefresh()
})

// Expose refresh method
defineExpose({
  refresh: loadAlerts
})
</script>
