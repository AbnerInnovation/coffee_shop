import api from './api';

// Types
export type PeriodType = 'today' | 'week' | 'month' | 'custom';

export interface TopProduct {
  product_id: number;
  product_name: string;
  category_id: number;
  quantity_sold: number;
  total_revenue: number;
  percentage_of_sales: number;
}

export interface TopProductsReport {
  period: {
    start_date: string | null;
    end_date: string | null;
  };
  total_products: number;
  total_revenue: number;
  top_products: TopProduct[];
}

export interface PaymentBreakdown {
  [key: string]: {
    amount: number;
    percentage: number;
    count: number;
  };
}

export interface DashboardSummary {
  period: {
    type: string;
    start_date: string;
    end_date: string;
    start_datetime: string;
    end_datetime: string;
  };
  sales_summary: {
    total_sales: number;
    total_tickets: number;
    average_ticket: number;
  };
  top_products: Array<{
    id: number;
    name: string;
    category_name: string;
    quantity_sold: number;
  }>;
  payment_breakdown: PaymentBreakdown;
  cash_register: {
    open_sessions: number;
    closed_sessions: number;
    total_cash_collected: number;
  };
  inventory_alerts: {
    unavailable_count: number;
    unavailable_products: Array<{
      id: number;
      name: string;
      category_id: number;
    }>;
  };
}

export interface SalesTrendData {
  date: string;
  orders_count: number;
  total_sales: number;
  average_ticket: number;
}

export interface SalesTrendReport {
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  trend: SalesTrendData[];
}

// Service methods
export const reportsService = {
  /**
   * Get top selling products
   */
  async getTopProducts(params?: {
    start_date?: string;
    end_date?: string;
    category_id?: number;
    limit?: number;
  }): Promise<TopProductsReport> {
    return await api.get('/reports/top-products', { params });
  },

  /**
   * Get unified dashboard with all metrics
   */
  async getDashboard(params?: {
    period?: PeriodType;
    start_date?: string;
    end_date?: string;
  }): Promise<DashboardSummary> {
    return await api.get('/reports/dashboard', { params });
  },

  /**
   * Get sales trend for charts
   */
  async getSalesTrend(days: number = 7): Promise<SalesTrendReport> {
    return await api.get('/reports/sales-trend', {
      params: { days }
    });
  },

  /**
   * Export dashboard to CSV (client-side)
   */
  exportDashboardToCSV(dashboard: DashboardSummary): void {
    // Payment method translations
    const paymentMethodNames: Record<string, string> = {
      'cash': 'Efectivo',
      'card': 'Tarjeta',
      'digital': 'Digital',
      'other': 'Otro'
    };

    const rows = [
      ['Cloud Restaurant - Reporte de Dashboard'],
      [''],
      ['Período', `${dashboard.period.start_date} a ${dashboard.period.end_date}`],
      [''],
      ['RESUMEN DE VENTAS'],
      ['Ventas Totales', dashboard.sales_summary.total_sales.toFixed(2)],
      ['Total de Tickets', dashboard.sales_summary.total_tickets.toString()],
      ['Ticket Promedio', dashboard.sales_summary.average_ticket.toFixed(2)],
      [''],
      ['PRODUCTOS MÁS VENDIDOS'],
      ['Posición', 'Producto', 'Cantidad Vendida'],
      ...dashboard.top_products.map((p, i) => [
        (i + 1).toString(),
        p.name,
        p.quantity_sold.toString()
      ]),
      [''],
      ['DESGLOSE POR MÉTODO DE PAGO'],
      ['Método', 'Monto', 'Porcentaje', 'Cantidad'],
      ...Object.entries(dashboard.payment_breakdown).map(([method, data]) => [
        paymentMethodNames[method] || method,
        data.amount.toFixed(2),
        `${data.percentage.toFixed(2)}%`,
        data.count.toString()
      ]),
      [''],
      ['CAJA REGISTRADORA'],
      ['Sesiones Abiertas', dashboard.cash_register.open_sessions.toString()],
      ['Sesiones Cerradas', dashboard.cash_register.closed_sessions.toString()],
      ['Total Efectivo Recaudado', dashboard.cash_register.total_cash_collected.toFixed(2)],
      [''],
      ['ALERTAS DE INVENTARIO'],
      ['Productos No Disponibles', dashboard.inventory_alerts.unavailable_count.toString()],
      ...dashboard.inventory_alerts.unavailable_products.map(p => ['', p.name])
    ];

    const csvContent = rows.map(row => row.join(',')).join('\n');
    // Add BOM (Byte Order Mark) for UTF-8 to ensure proper encoding in Excel
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `dashboard-report-${dashboard.period.start_date}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  /**
   * Print dashboard report
   */
  printDashboard(): void {
    window.print();
  }
};

export default reportsService;
