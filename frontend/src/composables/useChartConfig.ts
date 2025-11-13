import { useI18n } from 'vue-i18n'

/**
 * Composable para configuraciones de gráficas de Chart.js
 */
export function useChartConfig() {
  const { t } = useI18n()

  /**
   * Formatea números con separador de miles
   */
  function formatNumber(num: number, decimals: number = 2): string {
    return num.toLocaleString('es-MX', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    })
  }

  /**
   * Configuración para gráficas de barras horizontales
   */
  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y' as const,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: ${context.parsed.x}`
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
          color: '#6b7280'
        }
      }
    }
  }

  /**
   * Configuración para gráficas de dona
   */
  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#6b7280',
          font: {
            size: 13,
            weight: 500
          },
          padding: 15,
          generateLabels: function(chart: any) {
            const data = chart.data
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label: string, i: number) => {
                const value = data.datasets[0].data[i]
                const formattedValue = formatNumber(value)
                return {
                  text: `${label}: $${formattedValue}`,
                  fillStyle: data.datasets[0].backgroundColor[i],
                  fontColor: '#6b7280',
                  hidden: false,
                  index: i
                }
              })
            }
            return []
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.label || ''
            const value = context.parsed
            const formattedValue = formatNumber(value)
            const percentage = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
            const percent = ((value / percentage) * 100).toFixed(1)
            return `${label}: $${formattedValue} (${percent}%)`
          }
        }
      }
    }
  }

  /**
   * Configuración para gráficas de línea
   */
  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: '#6b7280',
          font: {
            size: 13
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#6b7280'
        }
      },
      y: {
        beginAtZero: true,
        ticks: {
          color: '#6b7280'
        }
      }
    }
  }

  /**
   * Colores predefinidos para gráficas
   */
  const chartColors = {
    primary: 'rgba(79, 70, 229, 0.8)',
    primaryBorder: 'rgba(79, 70, 229, 1)',
    green: 'rgba(34, 197, 94, 0.8)',
    greenBorder: 'rgba(34, 197, 94, 1)',
    blue: 'rgba(59, 130, 246, 0.8)',
    blueBorder: 'rgba(59, 130, 246, 1)',
    purple: 'rgba(168, 85, 247, 0.8)',
    purpleBorder: 'rgba(168, 85, 247, 1)',
    orange: 'rgba(251, 146, 60, 0.8)',
    orangeBorder: 'rgba(251, 146, 60, 1)'
  }

  return {
    formatNumber,
    barChartOptions,
    doughnutOptions,
    lineChartOptions,
    chartColors
  }
}
