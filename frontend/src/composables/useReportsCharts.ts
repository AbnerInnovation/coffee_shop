import { computed, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DashboardSummary, SalesTrendReport } from '@/services/reportsService'
import { useChartConfig } from './useChartConfig'

/**
 * Composable para datos de gráficas de reportes
 */
export function useReportsCharts(
  dashboard: Ref<DashboardSummary | null>,
  salesTrend: Ref<SalesTrendReport | null>
) {
  const { t } = useI18n()
  const { chartColors } = useChartConfig()

  /**
   * Datos para gráfica de productos más vendidos
   */
  const topProductsChartData = computed(() => {
    if (!dashboard.value) return { labels: [], datasets: [] }
    
    return {
      labels: dashboard.value.top_products.map(p => `${p.name} (${p.category_name})`),
      datasets: [
        {
          label: t('app.reports.quantity_sold'),
          data: dashboard.value.top_products.map(p => p.quantity_sold),
          backgroundColor: chartColors.primary,
          borderColor: chartColors.primaryBorder,
          borderWidth: 1
        }
      ]
    }
  })

  /**
   * Datos para gráfica de métodos de pago
   */
  const paymentChartData = computed(() => {
    if (!dashboard.value) return { labels: [], datasets: [] }
    
    const breakdown = dashboard.value.payment_breakdown
    const labels = Object.keys(breakdown).map(key => t(`app.reports.payment_${key}`))
    const data = Object.values(breakdown).map(v => v.amount)
    
    return {
      labels,
      datasets: [
        {
          data,
          backgroundColor: [
            chartColors.green,
            chartColors.blue,
            chartColors.purple,
            chartColors.orange
          ],
          borderColor: [
            chartColors.greenBorder,
            chartColors.blueBorder,
            chartColors.purpleBorder,
            chartColors.orangeBorder
          ],
          borderWidth: 1
        }
      ]
    }
  })

  /**
   * Datos para gráfica de tendencia de ventas
   */
  const salesTrendChartData = computed(() => {
    if (!salesTrend.value) return { labels: [], datasets: [] }
    
    return {
      labels: salesTrend.value.trend.map(t => t.date),
      datasets: [
        {
          label: t('app.reports.daily_sales'),
          data: salesTrend.value.trend.map(t => t.total_sales),
          borderColor: chartColors.primaryBorder,
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    }
  })

  return {
    topProductsChartData,
    paymentChartData,
    salesTrendChartData
  }
}
