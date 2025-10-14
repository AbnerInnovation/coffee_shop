<template>
  <div>
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Stats Cards -->
      <div class="overflow-hidden rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('app.dashboard.total_orders_today') }}</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900 dark:text-white">{{ stats.totalOrdersToday }}</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('app.dashboard.revenue_today') }}</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900 dark:text-white">${{ stats.revenueToday.toFixed(2) }}</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('app.dashboard.active_tables') }}</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900 dark:text-white">{{ stats.activeTables }}/{{ stats.totalTables }}</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500 dark:text-gray-400">{{ t('app.dashboard.popular_item') }}</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900 dark:text-white">{{ stats.popularItem || '—' }}</dd>
      </div>
    </div>
    
    <div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Recent Orders -->
      <div class="overflow-hidden rounded-lg bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow">
        <div class="border-b border-gray-200 dark:border-gray-800 px-4 py-5 sm:px-6">
          <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{{ t('app.dashboard.recent_orders') }}</h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.order_number') }}</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.table') }}</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.status') }}</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.amount') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-800 bg-white dark:bg-gray-900">
                <tr v-for="order in recentOrders" :key="order.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/60">
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm font-medium text-gray-900 dark:text-gray-100">#{{ order.id }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900 dark:text-gray-100">{{ order.table }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <span :class="getStatusBadgeClass(order.status)" class="inline-flex rounded-full px-2 text-xs font-semibold leading-5">
                      {{ t('app.status.' + String(order.status).toLowerCase()) }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    ${{ order.amount.toFixed(2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-4 text-right">
            <router-link to="/orders" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
              {{ t('app.actions.view_all_orders') }}
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Low Stock Items (derived from menu availability) -->
      <div v-if="false" class="overflow-hidden rounded-lg bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 shadow">
        <div class="border-b border-gray-200 dark:border-gray-800 px-4 py-5 sm:px-6">
          <h3 class="text-lg font-medium leading-6 text-gray-900 dark:text-white">{{ t('app.dashboard.low_stock_items') }}</h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
              <thead class="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.item') }}</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.category') }}</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.stock') }}</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">{{ t('app.dashboard.status') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-800 bg-white dark:bg-gray-900">
                <tr v-for="item in lowStockItems" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/60">
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="flex items-center">
                      <div class="h-10 w-10 flex-shrink-0">
                        <img class="h-10 w-10 rounded-full" :src="item.image || 'https://via.placeholder.com/40'" :alt="item.name" />
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.name }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900 dark:text-gray-100">{{ item.category }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900 dark:text-gray-100">{{ item.stock }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <span :class="getStockStatusClass(item.stock)" class="inline-flex rounded-full px-2 text-xs font-semibold leading-5">
                      {{ getStockStatusLabel(item.stock) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-4 text-right">
            <router-link to="/menu" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
              {{ t('app.actions.view_inventory') }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import orderService from '@/services/orderService';
import menuService from '@/services/menuService';
import tableService from '@/services/tableService';
import { useI18n } from 'vue-i18n';

type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';

const loading = ref(false);
const error = ref<string | null>(null);
const { t } = useI18n();

const stats = ref({
  totalOrdersToday: 0,
  revenueToday: 0,
  activeTables: 0,
  totalTables: 0,
  popularItem: '' as string | null
});

const recentOrders = ref<{ id: number; table: string; status: string; amount: number; createdAt: Date }[]>([]);
const lowStockItems = ref<{ id: number | string; name: string; category: string; stock: number; image?: string }[]>([]);

function getStatusBadgeClass(status: BackendOrderStatus | string) {
  const statusClasses = {
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Preparing': 'bg-blue-100 text-blue-800',
    'Ready': 'bg-green-100 text-green-800',
    'Completed': 'bg-gray-100 text-gray-800',
    'Cancelled': 'bg-red-100 text-red-800',
    // backend lowercase mapping
    'pending': 'bg-yellow-100 text-yellow-800',
    'preparing': 'bg-blue-100 text-blue-800',
    'ready': 'bg-green-100 text-green-800',
    'completed': 'bg-gray-100 text-gray-800',
    'cancelled': 'bg-red-100 text-red-800',
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

function getStockStatusClass(stock: number) {
  if (stock === 0) return 'bg-red-100 text-red-800';
  if (stock <= 3) return 'bg-yellow-100 text-yellow-800';
  return 'bg-green-100 text-green-800';
}

function getStockStatusLabel(stock: number) {
  if (stock === 0) return t('app.status.out_of_stock');
  if (stock <= 3) return t('app.status.low_stock');
  return t('app.status.in_stock');
}

function isToday(dateStr: string | Date) {
  const d = new Date(dateStr);
  const now = new Date();
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
}

onMounted(async () => {
  try {
    loading.value = true;
    error.value = null;

    // Fetch orders (limit 50 for dashboard)
    const orders = await orderService.getActiveOrders();
    const todayOrders = Array.isArray(orders) ? orders.filter(o => isToday(o.created_at)) : [];

    stats.value.totalOrdersToday = todayOrders.length;
    stats.value.revenueToday = todayOrders.reduce((sum, o) => sum + (o.total_amount || 0), 0);

    // Popular item by frequency in today's orders
    const freq: Record<string, number> = {};
    for (const o of todayOrders) {
      if (Array.isArray(o.items)) {
        for (const it of o.items) {
          const name = it.menu_item?.name || 'Unknown Item';
          freq[name] = (freq[name] || 0) + (it.quantity || 1);
        }
      }
    }
    const popular = Object.entries(freq).sort((a,b) => b[1]-a[1])[0]?.[0] || '';
    stats.value.popularItem = popular || null;

    // Recent orders table: pick 5 most recent
    const sorted = [...todayOrders].sort((a,b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime());
    recentOrders.value = sorted.slice(0,5).map(o => ({
      id: o.id,
      table: o.table_number ? t('app.dashboard.table_number', { number: o.table_number }) : (o.customer_name ? t('app.dashboard.takeaway') : t('app.dashboard.dine_in')),
      status: o.status,
      amount: o.total_amount || 0,
      createdAt: new Date(o.created_at || Date.now())
    }));

    // Tables
    const tables = await tableService.getTables();
    stats.value.totalTables = Array.isArray(tables) ? tables.length : 0;
    stats.value.activeTables = Array.isArray(tables) ? tables.filter(t => t.is_occupied).length : 0;

    // Low stock: derive from menu items that are unavailable
    const menuItems = await menuService.getMenuItems();
    lowStockItems.value = (menuItems || [])
      .filter(mi => mi.is_available === false || mi.isAvailable === false)
      .slice(0,5)
      .map(mi => ({
        id: mi.id,
        name: mi.name,
        category: typeof mi.category === 'string' ? mi.category : (mi.category?.name || ''),
        stock: 0,
        image: mi.image_url
      }));
  } catch (e) {
    console.error('Dashboard load failed:', e);
    error.value = t('app.messages.dashboard_load_failed');
  } finally {
    loading.value = false;
  }
});
</script>
