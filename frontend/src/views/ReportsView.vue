<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-4 sm:mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ t('app.reports.title') }}
            </h1>
            <p class="mt-1 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
              {{ t('app.reports.subtitle') }}
            </p>
            <p v-if="dashboard" class="mt-0.5 text-xs sm:text-sm font-medium text-indigo-600 dark:text-indigo-400 print:text-black">
              {{ dashboard.period.start_date }} - {{ dashboard.period.end_date }}
            </p>
          </div>
        </div>

        <!-- Period Selector -->
        <div class="mt-3 sm:mt-4 flex flex-wrap items-center gap-2 sm:gap-4">
          <div class="flex flex-wrap sm:flex-nowrap rounded-md shadow-sm gap-1 sm:gap-0">
            <button
              v-for="period in periods"
              :key="period.value"
              @click="handlePeriodChange(period.value)"
              :class="[
                'px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium',
                selectedPeriod === period.value
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
                period.value === 'today' ? 'rounded-l-md' : '',
                period.value === 'custom' ? 'rounded-r-md' : '',
                'border border-gray-300 dark:border-gray-600'
              ]"
            >
              {{ period.label }}
            </button>
          </div>

          <!-- Custom Date Range -->
          <div v-if="selectedPeriod === 'custom'" class="w-full">
            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-2">
              <input
                v-model="customStartDate"
                type="date"
                class="flex-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm px-4 py-2.5"
              />
              <span class="text-gray-500 dark:text-gray-400 text-sm">{{ t('app.reports.to') }}</span>
              <input
                v-model="customEndDate"
                type="date"
                class="flex-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm px-4 py-2.5"
              />
              <button
                @click="loadDashboard"
                class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 w-full sm:w-auto"
              >
                {{ t('app.reports.apply') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-md bg-red-50 dark:bg-red-900/20 p-4">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
              {{ t('app.reports.error_loading') }}
            </h3>
            <p class="mt-2 text-sm text-red-700 dark:text-red-300">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div v-else-if="dashboard" class="space-y-4 sm:space-y-6">
        <!-- Sales Summary Cards -->
        <div class="grid grid-cols-2 gap-3 sm:gap-4 sm:grid-cols-3">
          <StatCard
            :icon="CurrencyDollarIcon"
            :label="t('app.reports.total_sales')"
            :value="dashboard.sales_summary.total_sales"
            icon-color="green"
          />
          
          <StatCard
            :icon="ReceiptPercentIcon"
            :label="t('app.reports.total_tickets')"
            :value="dashboard.sales_summary.total_tickets"
            :decimals="0"
            prefix=""
            icon-color="blue"
          />
          
          <StatCard
            :icon="ChartBarIcon"
            :label="t('app.reports.average_ticket')"
            :value="dashboard.sales_summary.average_ticket"
            icon-color="purple"
            full-width
          />
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <ChartCard
            :title="t('app.reports.top_products')"
            :has-data="dashboard.top_products.length > 0"
            :empty-message="t('app.reports.no_data')"
          >
            <Bar :data="topProductsChartData" :options="barChartOptions" />
          </ChartCard>

          <ChartCard
            :title="t('app.reports.payment_breakdown')"
            :has-data="Object.keys(dashboard.payment_breakdown).length > 0"
            :empty-message="t('app.reports.no_data')"
            height="sm"
          >
            <Doughnut :data="paymentChartData" :options="doughnutOptions" />
          </ChartCard>
        </div>

        <!-- Sales Trend Chart -->
        <div v-if="salesTrend" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
            {{ t('app.reports.sales_trend') }}
          </h3>
          <Line :data="salesTrendChartData" :options="lineChartOptions" />
        </div>

        <!-- Additional Info Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Cash Register Summary -->
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <BanknotesIcon class="h-5 w-5 mr-2 text-green-600" />
              {{ t('app.reports.cash_register') }}
            </h3>
            <dl class="space-y-3">
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.reports.open_sessions') }}
                </dt>
                <dd class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ dashboard.cash_register.open_sessions }}
                </dd>
              </div>
              <div class="flex justify-between">
                <dt class="text-sm text-gray-500 dark:text-gray-400">
                  {{ t('app.reports.closed_sessions') }}
                </dt>
                <dd class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ dashboard.cash_register.closed_sessions }}
                </dd>
              </div>
              <div class="flex justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {{ t('app.reports.total_cash_collected') }}
                </dt>
                <dd class="text-sm font-semibold text-green-600 dark:text-green-400">
                  ${{ formatNumber(dashboard.cash_register.total_cash_collected) }}
                </dd>
              </div>
            </dl>
          </div>

          <!-- Inventory Alerts -->
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <ExclamationTriangleIcon class="h-5 w-5 mr-2 text-amber-600" />
              {{ t('app.reports.inventory_alerts') }}
            </h3>
            <div v-if="dashboard.inventory_alerts.unavailable_count > 0">
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {{ t('app.reports.unavailable_products_count', { count: dashboard.inventory_alerts.unavailable_count }) }}
              </p>
              <ul class="space-y-2 max-h-40 overflow-y-auto">
                <li
                  v-for="product in dashboard.inventory_alerts.unavailable_products"
                  :key="product.id"
                  class="text-sm text-gray-700 dark:text-gray-300 flex items-center"
                >
                  <span class="h-2 w-2 bg-red-500 rounded-full mr-2"></span>
                  {{ product.name }}
                </li>
              </ul>
            </div>
            <div v-else class="text-center py-8">
              <CheckCircleIcon class="h-12 w-12 text-green-500 mx-auto mb-2" />
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ t('app.reports.all_products_available') }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  CurrencyDollarIcon,
  ReceiptPercentIcon,
  ChartBarIcon,
  BanknotesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'
import { useReportsData } from '@/composables/useReportsData'
import { useReportsCharts } from '@/composables/useReportsCharts'
import { useChartConfig } from '@/composables/useChartConfig'
import StatCard from '@/components/reports/StatCard.vue'
import ChartCard from '@/components/reports/ChartCard.vue'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

const { t } = useI18n()

// Data management
const {
  loading,
  error,
  dashboard,
  salesTrend,
  selectedPeriod,
  customStartDate,
  customEndDate,
  periods,
  handlePeriodChange,
  loadDashboard
} = useReportsData()

// Chart data
const {
  topProductsChartData,
  paymentChartData,
  salesTrendChartData
} = useReportsCharts(dashboard, salesTrend)

// Chart configuration
const {
  formatNumber,
  barChartOptions,
  doughnutOptions,
  lineChartOptions
} = useChartConfig()

// Lifecycle
onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
@media print {
  button {
    display: none !important;
  }
  
  * {
    background: white !important;
    color: black !important;
    border-color: #d1d5db !important;
  }
  
  .shadow {
    box-shadow: none !important;
    border: 1px solid #d1d5db !important;
  }
  
  h1, h2, h3, h4, h5, h6, p, span, div, dt, dd {
    color: black !important;
  }
  
  svg {
    color: #374151 !important;
  }
}
</style>
