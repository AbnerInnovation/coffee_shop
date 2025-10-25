import { ref } from 'vue';
import orderService from '@/services/orderService';
import tableService from '@/services/tableService';
import { useI18n } from 'vue-i18n';

export interface DashboardStats {
  totalOrdersToday: number;
  revenueToday: number;
  activeTables: number;
  totalTables: number;
  popularItem: string | null;
  ordersComparison: number | null;
  revenueComparison: number | null;
}

export interface KitchenStats {
  ordersInQueue: number;
  avgPrepTime: string;
  longestWait: string;
}

export function useDashboardStats() {
  const { t } = useI18n();
  const loading = ref(false);
  const error = ref<string | null>(null);

  const stats = ref<DashboardStats>({
    totalOrdersToday: 0,
    revenueToday: 0,
    activeTables: 0,
    totalTables: 0,
    popularItem: null,
    ordersComparison: null,
    revenueComparison: null
  });

  const kitchenStats = ref<KitchenStats>({
    ordersInQueue: 0,
    avgPrepTime: '—',
    longestWait: '—'
  });

  // Date utility functions
  function isToday(dateStr: string | Date): boolean {
    const d = new Date(dateStr);
    const now = new Date();
    return d.getFullYear() === now.getFullYear() && 
           d.getMonth() === now.getMonth() && 
           d.getDate() === now.getDate();
  }

  function isYesterday(dateStr: string | Date): boolean {
    const d = new Date(dateStr);
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return d.getFullYear() === yesterday.getFullYear() && 
           d.getMonth() === yesterday.getMonth() && 
           d.getDate() === yesterday.getDate();
  }

  function getMinutesSince(dateStr: string | Date): number {
    const d = new Date(dateStr);
    const now = new Date();
    return Math.floor((now.getTime() - d.getTime()) / (1000 * 60));
  }

  // Calculate order statistics
  function calculateOrderStats(todayOrders: any[], yesterdayOrders: any[]) {
    stats.value.totalOrdersToday = todayOrders.length;
    stats.value.revenueToday = todayOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0);
    
    const yesterdayOrderCount = yesterdayOrders.length;
    const yesterdayRevenue = yesterdayOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0);
    
    stats.value.ordersComparison = stats.value.totalOrdersToday - yesterdayOrderCount;
    stats.value.revenueComparison = stats.value.revenueToday - yesterdayRevenue;
  }

  // Calculate kitchen performance metrics
  function calculateKitchenStats(todayOrders: any[]) {
    const activeOrders = todayOrders.filter(o => o.status === 'pending' || o.status === 'preparing');
    kitchenStats.value.ordersInQueue = activeOrders.length;
    
    // Calculate average prep time for completed orders today
    const completedToday = todayOrders.filter(o => o.status === 'completed' || o.status === 'ready');
    if (completedToday.length > 0) {
      const totalPrepTime = completedToday.reduce((sum, o) => {
        const created = new Date(o.created_at);
        const updated = new Date(o.updated_at || o.created_at);
        return sum + Math.floor((updated.getTime() - created.getTime()) / (1000 * 60));
      }, 0);
      kitchenStats.value.avgPrepTime = Math.round(totalPrepTime / completedToday.length).toString();
    } else {
      kitchenStats.value.avgPrepTime = '—';
    }
    
    // Find longest waiting order
    if (activeOrders.length > 0) {
      const waitTimes = activeOrders.map(o => getMinutesSince(o.created_at));
      kitchenStats.value.longestWait = Math.max(...waitTimes).toString();
    } else {
      kitchenStats.value.longestWait = '—';
    }
  }

  // Calculate popular item
  function calculatePopularItem(todayOrders: any[]) {
    const freq: Record<string, number> = {};
    
    for (const order of todayOrders) {
      if (Array.isArray(order.items)) {
        for (const item of order.items) {
          const name = item.menu_item?.name || 'Unknown Item';
          freq[name] = (freq[name] || 0) + (item.quantity || 1);
        }
      }
    }
    
    const popular = Object.entries(freq).sort((a, b) => b[1] - a[1])[0]?.[0] || '';
    stats.value.popularItem = popular || null;
  }

  // Calculate table statistics
  async function calculateTableStats() {
    const tables = await tableService.getTables();
    stats.value.totalTables = Array.isArray(tables) ? tables.length : 0;
    stats.value.activeTables = Array.isArray(tables) ? tables.filter(t => t.is_occupied).length : 0;
  }

  // Main load function
  async function loadStats() {
    try {
      loading.value = true;
      error.value = null;

      // Fetch orders
      const orders = await orderService.getActiveOrders();
      const todayOrders = Array.isArray(orders) ? orders.filter(o => isToday(o.created_at)) : [];
      const yesterdayOrders = Array.isArray(orders) ? orders.filter(o => isYesterday(o.created_at)) : [];

      // Calculate all statistics
      calculateOrderStats(todayOrders, yesterdayOrders);
      calculateKitchenStats(todayOrders);
      calculatePopularItem(todayOrders);
      await calculateTableStats();

    } catch (e) {
      console.error('Dashboard load failed:', e);
      error.value = t('app.messages.dashboard_load_failed');
    } finally {
      loading.value = false;
    }
  }

  return {
    stats,
    kitchenStats,
    loading,
    error,
    loadStats
  };
}
