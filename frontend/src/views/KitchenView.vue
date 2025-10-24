<template>
  <MainLayout>
    <div class="kitchen-view space-y-4 sm:space-y-6">
      <PageHeader
        :title="t('app.views.kitchen.title')"
        :subtitle="t('app.views.kitchen.last_updated', { time: new Date().toLocaleTimeString() })"
      />

      <!-- Status Tabs -->
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="-mb-px flex space-x-8 px-4" aria-label="Tabs">
            <button
              v-for="tab in statusTabs"
              :key="tab.value"
              @click="selectedStatus = tab.value as 'all' | 'pending' | 'preparing'"
              :class="[
                selectedStatus === tab.value
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              {{ tab.label }}
              <span
                v-if="tab.count > 0"
                :class="[
                  selectedStatus === tab.value
                    ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400'
                    : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-300',
                  'ml-2 py-0.5 px-2.5 rounded-full text-xs font-medium'
                ]"
              >
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>
      </div>

    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>

    <div v-else>
      <div v-if="filteredOrders.length === 0" class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('app.views.kitchen.no_active') }}</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.kitchen.no_active_description') }}</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <div v-for="order in filteredOrders" :key="order.id" class="bg-white dark:bg-gray-900 dark:border-gray-700 border-gray-200 border-2 rounded-lg shadow-md overflow-hidden">
          <div class="p-3 sm:p-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex justify-between items-start gap-2">
              <div class="flex-1 min-w-0">
                <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white truncate">{{ t('app.views.kitchen.order', { id: order.id }) }}</h3>
                <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {{ formatTime(order.created_at) }}
                  <span v-if="order.table_number" class="ml-1 sm:ml-2">• {{ t('app.views.kitchen.table', { number: order.table_number }) }}</span>
                </p>
              </div>
              <span 
                class="flex-shrink-0 px-2 py-1 text-xs font-medium rounded-full"
                :class="getStatusBadgeClass(order.status)"
              >
                {{ t(`app.status.${order.status}`) }}
              </span>
            </div>
            <div v-if="order.notes" class="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 text-xs sm:text-sm text-yellow-700 dark:text-yellow-300 rounded">
              {{ order.notes }}
            </div>
          </div>

          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div 
              v-for="item in getPendingItems(order)" 
              :key="item.id"
              class="p-3 sm:p-4"
              :class="{
                'bg-yellow-50 dark:bg-yellow-900/20': item.status === 'pending',
                'bg-blue-50 dark:bg-blue-900/20': item.status === 'preparing',
                'bg-green-50 dark:bg-green-900/20': item.status === 'ready'
              }"
            >
              <div class="flex justify-between items-start gap-2">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center flex-wrap gap-2">
                    <span class="font-semibold text-base sm:text-lg text-gray-900 dark:text-white">{{ item.quantity }}x</span>
                    <span class="text-base sm:text-lg text-gray-900 dark:text-white">{{ item.menu_item.name }}</span>
                    <span v-if="item.variant" class="text-sm sm:text-base text-gray-600 dark:text-gray-400">({{ item.variant.name }})</span>
                    
                    <!-- Item Status Badge -->
                    <span 
                      class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                      :class="getItemStatusBadgeClass(item.status)"
                    >
                      {{ t(`app.status.${item.status}`) }}
                    </span>
                  </div>
                  
                  <div v-if="item.menu_item.category" class="mt-1">
                    <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
                      {{ item.menu_item.category }}
                    </span>
                  </div>
                  
                  <div v-if="item.special_instructions" class="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs sm:text-sm text-blue-700 dark:text-blue-300">
                     {{ item.special_instructions }}
                  </div>
                  
                  <!-- Item Action Buttons -->
                  <div class="mt-2 flex gap-2">
                    <button
                      v-if="item.status === 'pending'"
                      @click="markItemPreparing(order, item)"
                      class="text-xs sm:text-sm px-3 py-1 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    >
                      {{ t('app.views.kitchen.actions.start_preparing') }}
                    </button>
                    <button
                      v-if="item.status === 'preparing'"
                      @click="markItemReady(order, item)"
                      class="text-xs sm:text-sm px-3 py-1 rounded-md bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      {{ t('app.views.kitchen.actions.item_ready') }}
                    </button>
                  </div>
                </div>
                
                <div class="flex items-center flex-shrink-0">
                  <span class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-medium">
                    {{ getTimeElapsed(item.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="p-3 sm:p-4 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
            <!-- Bulk Actions for All Items -->
            <div class="space-y-2">
              <button
                v-if="hasPendingItems(order)"
                @click="startPreparingAllItems(order)"
                class="w-full bg-indigo-600 text-white py-2.5 sm:py-2 px-4 rounded-md hover:bg-indigo-700 active:bg-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 font-medium text-sm sm:text-base touch-manipulation"
              >
                {{ t('app.views.kitchen.actions.start_preparing_all') }}
              </button>
              <button
                v-if="hasPreparingItems(order)"
                @click="markAllItemsReady(order)"
                class="w-full bg-green-600 text-white py-2.5 sm:py-2 px-4 rounded-md hover:bg-green-700 active:bg-green-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 font-medium text-sm sm:text-base touch-manipulation"
              >
                {{ t('app.views.kitchen.actions.all_items_ready') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import orderService from '@/services/orderService';
import type { Order, OrderItem } from '@/services/orderService';

const loading = ref(true);
const activeOrders = ref<Order[]>([]);
const selectedStatus = ref<'all' | 'pending' | 'preparing'>('all');
let refreshInterval: number | null = null;

const { t } = useI18n();

// Status tabs with counts
const statusTabs = computed(() => [
  {
    value: 'all',
    label: t('app.views.kitchen.tabs.all'),
    count: activeOrders.value.length
  },
  {
    value: 'pending',
    label: t('app.views.kitchen.tabs.pending'),
    count: activeOrders.value.filter(o => o.status === 'pending').length
  },
  {
    value: 'preparing',
    label: t('app.views.kitchen.tabs.preparing'),
    count: activeOrders.value.filter(o => o.status === 'preparing').length
  }
]);

// Filtered orders based on selected status
const filteredOrders = computed(() => {
  if (selectedStatus.value === 'all') {
    return activeOrders.value;
  }
  return activeOrders.value.filter(order => order.status === selectedStatus.value);
});

// Format time for display
const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

// Format status for display
const formatStatus = (status: string) => {
  return t(`app.status.${status}`) as string;
};

// Get status badge class
const getStatusBadgeClass = (status: string) => {
  const classes = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200',
    'preparing': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200',
    'ready': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200',
    'completed': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

// Get item status badge class
const getItemStatusBadgeClass = (status: string) => {
  const classes = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200',
    'preparing': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200',
    'ready': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200',
    'delivered': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
  };
  return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800';
};

// Calculate time elapsed since item was started
const getTimeElapsed = (startedAt: string) => {
  if (!startedAt) return '';
  const start = new Date(startedAt).getTime();
  const now = new Date().getTime();
  const diffInMinutes = Math.floor((now - start) / (1000 * 60));
  if (diffInMinutes < 1) return t('app.views.kitchen.time.just_now') as string;
  if (diffInMinutes < 60) return t('app.views.kitchen.time.minutes_ago', { m: diffInMinutes }) as string;
  const hours = Math.floor(diffInMinutes / 60);
  const minutes = diffInMinutes % 60;
  return t('app.views.kitchen.time.hours_minutes_ago', { h: hours, m: minutes }) as string;
};

// Filter items to show only pending or preparing items (not completed, ready, or cancelled)
const getPendingItems = (order: Order) => {
  return order.items.filter(item => 
    item.status === 'pending' || item.status === 'preparing'
  );
};

// Check if order has pending items
const hasPendingItems = (order: Order) => {
  return getPendingItems(order).some(item => item.status === 'pending');
};

// Check if order has preparing items
const hasPreparingItems = (order: Order) => {
  return getPendingItems(order).some(item => item.status === 'preparing');
};

// Fetch active orders (pending or preparing)
const fetchActiveOrders = async () => {
  try {
    loading.value = true;
    const pendingOrders = await orderService.getActiveOrders('pending', undefined, 'kitchen');
    const preparingOrders = await orderService.getActiveOrders('preparing', undefined, 'kitchen');
    
    // Backend already orders by status (pending first) then by updated_at (FIFO)
    // Just combine the arrays
    const allOrders = [...pendingOrders, ...preparingOrders];
    
    // Initialize item statuses if not set
    activeOrders.value = allOrders.map(order => ({
      ...order,
      items: order.items.map(item => ({
        ...item,
        status: item.status || 'pending',
        started_at: (item as any).started_at || order.created_at
      }))
    }));
  } catch (error) {
    console.error('Error fetching active orders:', error);
  } finally {
    loading.value = false;
  }
};

// Mark individual item as preparing
const markItemPreparing = async (order: Order, item: OrderItem) => {
  try {
    // Update the item status
    await orderService.updateOrderItemStatus(order.id, item.id, 'preparing');
    
    // Fetch the updated order to get current state of all items
    const updatedOrder = await orderService.getOrder(order.id);
    
    // Check if all items are now preparing or beyond
    const allItemsPreparing = updatedOrder.items.every(i => 
      i.status === 'preparing' || 
      i.status === 'ready' || 
      i.status === 'delivered'
    );
    
    // Update order status to preparing if all items are preparing
    if (allItemsPreparing && updatedOrder.status === 'pending') {
      await orderService.updateOrder(order.id, { status: 'preparing' });
    }
    
    await fetchActiveOrders();
  } catch (error) {
    console.error('Error updating item status:', error);
  }
};

// Mark individual item as ready
const markItemReady = async (order: Order, item: OrderItem) => {
  try {
    // Update the item status
    await orderService.updateOrderItemStatus(order.id, item.id, 'ready');
    
    // Fetch the updated order to get current state of all items
    const updatedOrder = await orderService.getOrder(order.id);
    
    // Check if all items in the order are now ready or delivered
    const allItemsReady = updatedOrder.items.every(i => 
      i.status === 'ready' || 
      i.status === 'delivered' ||
      i.status === 'cancelled'
    );
    
    // Update order status to ready if all items are ready
    if (allItemsReady && updatedOrder.status !== 'ready') {
      await orderService.updateOrder(order.id, { status: 'ready' });
    }
    
    await fetchActiveOrders();
  } catch (error) {
    console.error('Error updating item status:', error);
  }
};

// Start preparing all pending items in an order
const startPreparingAllItems = async (order: Order) => {
  try {
    const pendingItems = getPendingItems(order).filter(item => item.status === 'pending');
    
    // Update all pending items to preparing
    for (const item of pendingItems) {
      await orderService.updateOrderItemStatus(order.id, item.id, 'preparing');
    }
    
    // Fetch the updated order to get current state of all items
    const updatedOrder = await orderService.getOrder(order.id);
    
    // Check if all items are now preparing or beyond
    const allItemsPreparing = updatedOrder.items.every(i => 
      i.status === 'preparing' || 
      i.status === 'ready' || 
      i.status === 'delivered'
    );
    
    // Update order status to preparing if all items are preparing
    if (allItemsPreparing && updatedOrder.status === 'pending') {
      await orderService.updateOrder(order.id, { status: 'preparing' });
    }
    
    await fetchActiveOrders();
  } catch (error) {
    console.error('Error starting preparation:', error);
  }
};

// Mark all preparing items as ready
const markAllItemsReady = async (order: Order) => {
  try {
    const preparingItems = getPendingItems(order).filter(item => item.status === 'preparing');
    
    // Update all preparing items to ready
    for (const item of preparingItems) {
      await orderService.updateOrderItemStatus(order.id, item.id, 'ready');
    }
    
    // Fetch the updated order to get current state of all items
    const updatedOrder = await orderService.getOrder(order.id);
    
    // Check if all items in the order are ready or delivered
    const allItemsReady = updatedOrder.items.every(item => 
      item.status === 'ready' || item.status === 'delivered' || item.status === 'cancelled'
    );
    
    // Update order status to ready if all items are ready
    if (allItemsReady && updatedOrder.status !== 'ready') {
      await orderService.updateOrder(order.id, { status: 'ready' });
    }
    
    await fetchActiveOrders();
  } catch (error) {
    console.error('Error marking items ready:', error);
  }
};


// Set up auto-refresh
const setupAutoRefresh = () => {
  // Initial fetch
  fetchActiveOrders();
  
  // Set up polling every 30 seconds
  refreshInterval = window.setInterval(fetchActiveOrders, 30000);
};

// Clean up on component unmount
onMounted(setupAutoRefresh);
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>

<style scoped>
.kitchen-view {
  max-width: 1800px;
  margin: 0 auto;
}

/* Add any additional styles here */
</style>
