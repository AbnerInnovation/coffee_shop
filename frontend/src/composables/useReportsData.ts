import { ref, computed, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import reportsService, { type DashboardSummary, type SalesTrendReport, type PeriodType } from '@/services/reportsService'

/**
 * Composable para gestión de datos de reportes
 */
export function useReportsData() {
  const { t } = useI18n()

  // State
  const loading = ref(false)
  const error = ref<string | null>(null)
  const dashboard = ref<DashboardSummary | null>(null)
  const salesTrend = ref<SalesTrendReport | null>(null)
  const selectedPeriod = ref<PeriodType>('today')
  const customStartDate = ref('')
  const customEndDate = ref('')

  // Period options
  const periods = computed(() => [
    { value: 'today', label: t('app.reports.today') },
    { value: 'week', label: t('app.reports.week') },
    { value: 'month', label: t('app.reports.month') },
    { value: 'custom', label: t('app.reports.custom') }
  ])

  /**
   * Maneja el cambio de período
   */
  function handlePeriodChange(period: string) {
    selectedPeriod.value = period as PeriodType
    
    if (period !== 'custom') {
      loadDashboard()
    } else {
      error.value = null
    }
  }

  /**
   * Carga los datos del dashboard
   */
  async function loadDashboard() {
    loading.value = true
    error.value = null
    
    try {
      const params: any = { period: selectedPeriod.value }
      
      if (selectedPeriod.value === 'custom') {
        if (!customStartDate.value || !customEndDate.value) {
          error.value = t('app.reports.error_custom_dates')
          return
        }
        params.start_date = customStartDate.value
        params.end_date = customEndDate.value
      }
      
      dashboard.value = await reportsService.getDashboard(params)
      
      const trendDays = selectedPeriod.value === 'today' ? 7 : 30
      salesTrend.value = await reportsService.getSalesTrend(trendDays)
      
    } catch (err: any) {
      error.value = err.message || t('app.reports.error_generic')
      console.error('Error loading dashboard:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Exporta el dashboard a CSV
   */
  function exportToCSV() {
    if (dashboard.value) {
      reportsService.exportDashboardToCSV(dashboard.value)
    }
  }

  /**
   * Imprime el reporte
   */
  function printReport() {
    reportsService.printDashboard()
  }

  return {
    loading,
    error,
    dashboard,
    salesTrend,
    selectedPeriod,
    customStartDate,
    customEndDate,
    periods,
    handlePeriodChange,
    loadDashboard,
    exportToCSV,
    printReport
  }
}
