<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
              {{ t('app.reports.title') }}
            </h1>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {{ t('app.reports.subtitle') }}
            </p>
            <p v-if="dashboard" class="mt-1 text-sm font-medium text-indigo-600 dark:text-indigo-400 print:text-black">
              {{ dashboard.period.start_date }} - {{ dashboard.period.end_date }}
            </p>
          </div>
          
          <!-- Action Buttons (Hidden) -->
          <!-- <div class="mt-4 sm:mt-0 flex space-x-3">
            <button
              @click="exportToCSV"
              :disabled="loading"
              class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <ArrowDownTrayIcon class="h-5 w-5 mr-2" />
              {{ t('app.reports.export_csv') }}
            </button>
            <button
              @click="printReport"
              :disabled="loading"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              <PrinterIcon class="h-5 w-5 mr-2" />
              {{ t('app.reports.print') }}
            </button>
          </div> -->
        </div>

        <!-- Period Selector -->
        <div class="mt-6 flex flex-wrap items-center gap-2 sm:gap-4">
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

          <!-- Custom Date Range (shown when custom is selected) -->
          <div v-if="selectedPeriod === 'custom'" class="w-full">
            <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-2">
              <div class="flex-1">
                <input
                  v-model="customStartDate"
                  type="date"
                  class="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm px-4 py-2.5"
                  placeholder="Fecha inicio"
                />
              </div>
              <span class="text-gray-500 dark:text-gray-400 text-sm text-center sm:text-left">{{ t('app.reports.to') }}</span>
              <div class="flex-1">
                <input
                  v-model="customEndDate"
                  type="date"
                  class="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm px-4 py-2.5"
                  placeholder="Fecha fin"
                />
              </div>
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
      <div v-else-if="dashboard" class="space-y-6">
        <!-- Sales Summary Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
          <!-- Total Sales -->
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <CurrencyDollarIcon class="h-6 w-6 text-green-600" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {{ t('app.reports.total_sales') }}
                    </dt>
                    <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                      ${{ formatNumber(dashboard.sales_summary.total_sales) }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Total Tickets -->
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <ReceiptPercentIcon class="h-6 w-6 text-blue-600" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {{ t('app.reports.total_tickets') }}
                    </dt>
                    <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                      {{ formatNumber(dashboard.sales_summary.total_tickets, 0) }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <!-- Average Ticket -->
          <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <ChartBarIcon class="h-6 w-6 text-purple-600" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {{ t('app.reports.average_ticket') }}
                    </dt>
                    <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                      ${{ formatNumber(dashboard.sales_summary.average_ticket) }}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Top Products Chart -->
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-4 sm:p-6">
            <h3 class="text-base sm:text-lg font-medium text-gray-900 dark:text-white mb-4">
              {{ t('app.reports.top_products') }}
            </h3>
            <div v-if="dashboard.top_products.length > 0" class="h-64 sm:h-80">
              <Bar :data="topProductsChartData" :options="chartOptions" />
            </div>
            <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
              {{ t('app.reports.no_data') }}
            </div>
          </div>

          <!-- Payment Breakdown Chart -->
          <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
              {{ t('app.reports.payment_breakdown') }}
            </h3>
            <div v-if="Object.keys(dashboard.payment_breakdown).length > 0">
              <Doughnut :data="paymentChartData" :options="doughnutOptions" />
            </div>
            <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
              {{ t('app.reports.no_data') }}
            </div>
          </div>
        </div>

        <!-- Sales Trend Chart (Full Width) -->
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
import { ref, computed, onMounted } from 'vue';
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
  BanknotesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon,
  PrinterIcon
} from '@heroicons/vue/24/outline';
import reportsService, { type DashboardSummary, type SalesTrendReport, type PeriodType } from '@/services/reportsService';

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

// Helper function to format numbers with thousands separator
const formatNumber = (num: number, decimals: number = 2): string => {
  return num.toLocaleString('es-MX', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

// State
const loading = ref(false);
const error = ref<string | null>(null);
const dashboard = ref<DashboardSummary | null>(null);
const salesTrend = ref<SalesTrendReport | null>(null);
const selectedPeriod = ref<PeriodType>('today');
const customStartDate = ref('');
const customEndDate = ref('');

// Period options
const periods = [
  { value: 'today', label: t('app.reports.today') },
  { value: 'week', label: t('app.reports.week') },
  { value: 'month', label: t('app.reports.month') },
  { value: 'custom', label: t('app.reports.custom') }
];

// Chart Data
const topProductsChartData = computed(() => {
  if (!dashboard.value) return { labels: [], datasets: [] };
  
  return {
    labels: dashboard.value.top_products.map(p => `${p.name} (${p.category_name})`),
    datasets: [
      {
        label: t('app.reports.quantity_sold'),
        data: dashboard.value.top_products.map(p => p.quantity_sold),
        backgroundColor: 'rgba(79, 70, 229, 0.8)',
        borderColor: 'rgba(79, 70, 229, 1)',
        borderWidth: 1
      }
    ]
  };
});

const paymentChartData = computed(() => {
  if (!dashboard.value) return { labels: [], datasets: [] };
  
  const breakdown = dashboard.value.payment_breakdown;
  const labels = Object.keys(breakdown).map(key => t(`app.reports.payment_${key}`));
  const data = Object.values(breakdown).map(v => v.amount);
  
  return {
    labels,
    datasets: [
      {
        data,
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(251, 146, 60, 0.8)'
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(168, 85, 247, 1)',
          'rgba(251, 146, 60, 1)'
        ],
        borderWidth: 1
      }
    ]
  };
});

const salesTrendChartData = computed(() => {
  if (!salesTrend.value) return { labels: [], datasets: [] };
  
  return {
    labels: salesTrend.value.trend.map(t => t.date),
    datasets: [
      {
        label: t('app.reports.daily_sales'),
        data: salesTrend.value.trend.map(t => t.total_sales),
        borderColor: 'rgba(79, 70, 229, 1)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        tension: 0.4,
        fill: true
      }
    ]
  };
});

// Chart Options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false, // Allow custom height
  indexAxis: 'y' as const, // Horizontal bar chart for better mobile view
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return `${context.dataset.label}: ${context.parsed.x}`;
        }
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    },
    y: {
      ticks: {
        autoSkip: false,
        font: {
          size: 11
        },
        color: '#6b7280' // Gray-500: balanced contrast for both light and dark mode
      }
    }
  }
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        color: '#6b7280', // Gray-500: balanced contrast for both modes
        font: {
          size: 13,
          weight: 500
        },
        padding: 15,
        generateLabels: function(chart: any) {
          const data = chart.data;
          if (data.labels.length && data.datasets.length) {
            return data.labels.map((label: string, i: number) => {
              const value = data.datasets[0].data[i];
              const formattedValue = formatNumber(value);
              return {
                text: `${label}: $${formattedValue}`,
                fillStyle: data.datasets[0].backgroundColor[i],
                fontColor: '#6b7280', // Gray-500 for each label
                hidden: false,
                index: i
              };
            });
          }
          return [];
        }
      }
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          const label = context.label || '';
          const value = context.parsed;
          const formattedValue = formatNumber(value);
          const percentage = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
          const percent = ((value / percentage) * 100).toFixed(1);
          return `${label}: $${formattedValue} (${percent}%)`;
        }
      }
    }
  }
};

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: {
        color: '#6b7280', // Gray-500 for better contrast
        font: {
          size: 13
        }
      }
    }
  },
  scales: {
    x: {
      ticks: {
        color: '#6b7280' // Gray-500 for x-axis labels (dates)
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        color: '#6b7280' // Gray-500 for y-axis labels (amounts)
      }
    }
  }
};

// Methods
function handlePeriodChange(period: string) {
  selectedPeriod.value = period as PeriodType;
  
  // Only load dashboard automatically if not custom period
  if (period !== 'custom') {
    loadDashboard();
  } else {
    // Clear error when switching to custom
    error.value = null;
  }
}

async function loadDashboard() {
  loading.value = true;
  error.value = null;
  
  try {
    const params: any = { period: selectedPeriod.value };
    
    if (selectedPeriod.value === 'custom') {
      if (!customStartDate.value || !customEndDate.value) {
        error.value = t('app.reports.error_custom_dates');
        return;
      }
      params.start_date = customStartDate.value;
      params.end_date = customEndDate.value;
    }
    
    // Load dashboard data
    dashboard.value = await reportsService.getDashboard(params);
    
    // Load sales trend (last 7 days for today, 30 for week/month)
    const trendDays = selectedPeriod.value === 'today' ? 7 : 30;
    salesTrend.value = await reportsService.getSalesTrend(trendDays);
    
  } catch (err: any) {
    error.value = err.message || t('app.reports.error_generic');
    console.error('Error loading dashboard:', err);
  } finally {
    loading.value = false;
  }
}

function exportToCSV() {
  if (dashboard.value) {
    reportsService.exportDashboardToCSV(dashboard.value);
  }
}

function printReport() {
  reportsService.printDashboard();
}

// Lifecycle
onMounted(() => {
  loadDashboard();
});
</script>

<style scoped>
@media print {
  /* Hide buttons and navigation */
  button {
    display: none !important;
  }
  
  /* Force light background and dark text for print */
  * {
    background: white !important;
    color: black !important;
    border-color: #d1d5db !important;
  }
  
  /* Ensure cards have visible borders */
  .shadow {
    box-shadow: none !important;
    border: 1px solid #d1d5db !important;
  }
  
  /* Make sure text is readable */
  h1, h2, h3, h4, h5, h6, p, span, div, dt, dd {
    color: black !important;
  }
  
  /* Icons should be dark */
  svg {
    color: #374151 !important;
  }
  
  /* Remove page padding for better use of space */
  .min-h-screen {
    min-height: auto !important;
    padding: 0 !important;
  }
  
  /* Reduce spacing */
  .py-8 {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
  }
  
  .mb-8 {
    margin-bottom: 1rem !important;
  }
  
  .space-y-6 > * + * {
    margin-top: 1rem !important;
  }
  
  .gap-6 {
    gap: 0.75rem !important;
  }
  
  .gap-5 {
    gap: 0.5rem !important;
  }
  
  /* Reduce card padding */
  .p-6, .p-5, .p-4 {
    padding: 0.75rem !important;
  }
  
  /* Compact header */
  h1 {
    font-size: 1.5rem !important;
    margin-bottom: 0.25rem !important;
  }
  
  h3 {
    font-size: 1rem !important;
    margin-bottom: 0.5rem !important;
  }
  
  /* Adjust page breaks */
  .grid {
    page-break-inside: avoid;
  }
  
  /* Compact grid spacing */
  .grid-cols-1 {
    gap: 0.5rem !important;
  }
}
</style>

<style>
/* Global print styles - not scoped */
@media print {
  /* Hide navbar and other UI elements */
  nav,
  header,
  .navbar,
  [role="navigation"] {
    display: none !important;
  }
  
  /* Remove margins from body */
  body {
    margin: 0 !important;
    padding: 0 !important;
  }
  
  /* Ensure main content uses full width with minimal padding */
  main {
    margin: 0 !important;
    padding: 0.5rem !important;
  }
  
  /* Reduce container padding */
  .max-w-7xl {
    max-width: 100% !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
  
  /* Compact page layout */
  .px-4, .px-6, .px-8 {
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
  }
}
</style>
