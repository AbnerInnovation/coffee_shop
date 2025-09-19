<template>
  <div>
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Stats Cards -->
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Total Orders Today</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">{{ stats.totalOrdersToday }}</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Revenue Today</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">${{ stats.revenueToday.toFixed(2) }}</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Active Tables</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">{{ stats.activeTables }}/{{ stats.totalTables }}</dd>
      </div>
      
      <div class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6">
        <dt class="truncate text-sm font-medium text-gray-500">Popular Item</dt>
        <dd class="mt-1 text-3xl font-semibold tracking-tight text-gray-900">{{ stats.popularItem || '—' }}</dd>
      </div>
    </div>
    
    <div class="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- Recent Orders -->
      <div class="overflow-hidden rounded-lg bg-white shadow">
        <div class="border-b border-gray-200 px-4 py-5 sm:px-6">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Recent Orders</h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Order #</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Table</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Amount</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="order in recentOrders" :key="order.id" class="hover:bg-gray-50">
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm font-medium text-gray-900">#{{ order.id }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900">{{ order.table }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <span :class="getStatusBadgeClass(order.status)" class="inline-flex rounded-full px-2 text-xs font-semibold leading-5">
                      {{ order.status }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    ${{ order.amount.toFixed(2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-4 text-right">
            <router-link to="/orders" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
              View all orders
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- Low Stock Items (derived from menu availability) -->
      <div class="overflow-hidden rounded-lg bg-white shadow">
        <div class="border-b border-gray-200 px-4 py-5 sm:px-6">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Low Stock Items</h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div class="overflow-hidden">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Item</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Category</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Stock</th>
                  <th scope="col" class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="item in lowStockItems" :key="item.id" class="hover:bg-gray-50">
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="flex items-center">
                      <div class="h-10 w-10 flex-shrink-0">
                        <img class="h-10 w-10 rounded-full" :src="item.image || 'https://via.placeholder.com/40'" :alt="item.name" />
                      </div>
                      <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">{{ item.name }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900">{{ item.category }}</div>
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <div class="text-sm text-gray-900">{{ item.stock }}</div>
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
            <router-link to="/inventory" class="text-sm font-medium text-indigo-600 hover:text-indigo-500">
              View inventory
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

type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';

const loading = ref(false);
const error = ref<string | null>(null);

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

function getStockStatusClass(stock) {
  if (stock === 0) return 'bg-red-100 text-red-800';
  if (stock <= 3) return 'bg-yellow-100 text-yellow-800';
  return 'bg-green-100 text-green-800';
}

function getStockStatusLabel(stock) {
  if (stock === 0) return 'Out of Stock';
  if (stock <= 3) return 'Low Stock';
  return 'In Stock';
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
      table: o.table_number ? `Table ${o.table_number}` : (o.customer_name ? 'Takeaway' : 'Dine-in'),
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
    error.value = 'Failed to load dashboard data';
  } finally {
    loading.value = false;
  }
});
</script>
