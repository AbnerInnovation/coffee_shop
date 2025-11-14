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
        <ReportsPeriodSelector
          :periods="periods"
          :selected-period="selectedPeriod"
          :custom-start-date="customStartDate"
          :custom-end-date="customEndDate"
          @period-change="handlePeriodChange"
          @update:custom-start-date="customStartDate = $event"
          @update:custom-end-date="customEndDate = $event"
          @apply="loadDashboard"
        />
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
        <ReportsAdditionalInfo
          :cash-register="dashboard.cash_register"
          :inventory-alerts="dashboard.inventory_alerts"
          :format-number="formatNumber"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
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
} from 'chart.js';
import { Bar, Doughnut, Line } from 'vue-chartjs';
import {
  CurrencyDollarIcon,
  ReceiptPercentIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline';
import { useReportsData } from '@/composables/useReportsData';
import { useReportsCharts } from '@/composables/useReportsCharts';
import { useChartConfig } from '@/composables/useChartConfig';
import StatCard from '@/components/reports/StatCard.vue';
import ChartCard from '@/components/reports/ChartCard.vue';
import ReportsPeriodSelector from '@/components/reports/ReportsPeriodSelector.vue';
import ReportsAdditionalInfo from '@/components/reports/ReportsAdditionalInfo.vue';

/**
 * ReportsView - Main view for reports and analytics
 * 
 * Displays comprehensive sales and operational reports including:
 * - Sales summary (total sales, tickets, average ticket)
 * - Top products chart
 * - Payment breakdown
 * - Sales trend over time
 * - Cash register summary
 * - Inventory alerts
 * 
 * Uses composables for data management, chart configuration, and business logic.
 */

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
);

const { t } = useI18n();

// Data management composable
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
} = useReportsData();

// Chart data composable
const {
  topProductsChartData,
  paymentChartData,
  salesTrendChartData
} = useReportsCharts(dashboard, salesTrend);

// Chart configuration composable
const {
  formatNumber,
  barChartOptions,
  doughnutOptions,
  lineChartOptions
} = useChartConfig();

// Lifecycle
onMounted(() => {
  loadDashboard();
});
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
