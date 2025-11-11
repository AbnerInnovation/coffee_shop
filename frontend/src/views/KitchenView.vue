<template>
  <MainLayout>
    <div class="kitchen-view space-y-4 sm:space-y-6">
      <PageHeader
        :title="t('app.views.kitchen.title')"
        :subtitle="t('app.views.kitchen.last_updated', { time: new Date().toLocaleTimeString() })"
      />

      <!-- Status Tabs -->
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow">
        <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
          <nav class="-mb-px flex space-x-2 sm:space-x-6 px-2 sm:px-3 min-w-max" aria-label="Tabs">
            <button
              v-for="tab in statusTabs"
              :key="tab.value"
              @click="selectedStatus = tab.value as 'all' | 'pending' | 'preparing' | 'grouped'"
              :class="[
                selectedStatus === tab.value
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                'whitespace-nowrap py-2 sm:py-3 px-2 border-b-2 font-semibold text-xs sm:text-base flex-shrink-0'
              ]"
            >
              {{ tab.label }}
              <span
                v-if="tab.count > 0"
                :class="[
                  selectedStatus === tab.value
                    ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400'
                    : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-300',
                  'ml-1 py-0.5 px-1.5 sm:px-2 rounded-full text-xs font-medium'
                ]"
              >
                {{ tab.count }}
              </span>
            </button>
          </nav>
        </div>
      </div>

      <!-- Order Type Filter Tabs -->
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow">
        <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
          <nav class="-mb-px flex space-x-2 sm:space-x-4 px-2 sm:px-3 min-w-max" aria-label="Order Type Filter">
            <button
              v-for="typeTab in orderTypeTabs"
              :key="typeTab.value"
              @click="selectedOrderType = typeTab.value as 'all' | 'dine_in' | 'takeaway' | 'delivery'"
              :class="[
                selectedOrderType === typeTab.value
                  ? 'border-green-500 text-green-600 dark:text-green-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                'whitespace-nowrap py-2 px-2 border-b-2 font-medium text-xs sm:text-sm flex-shrink-0'
              ]"
            >
              {{ typeTab.label }}
              <span
                v-if="typeTab.count > 0"
                :class="[
                  selectedOrderType === typeTab.value
                    ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-300',
                  'ml-1 py-0.5 px-1.5 rounded-full text-xs font-medium'
                ]"
              >
                {{ typeTab.count }}
              </span>
            </button>
          </nav>
        </div>
      </div>

    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>

    <div v-else>
      <!-- Grouped View -->
      <div v-if="selectedStatus === 'grouped'">
        <div v-if="groupedItems.length === 0" class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('app.views.kitchen.no_active') }}</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.kitchen.no_active_description') }}</p>
        </div>

        <div v-else class="bg-white dark:bg-gray-900 rounded-lg shadow-md overflow-hidden">
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div 
              v-for="item in groupedItems" 
              :key="`${item.menu_item_id}_${item.variant_id}`"
              class="p-4 sm:p-6 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-3 mb-2">
                    <span class="font-bold text-3xl sm:text-4xl text-indigo-600 dark:text-indigo-400">{{ item.total_quantity }}x</span>
                    <div class="flex-1">
                      <h3 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
                        {{ item.menu_item_name }}
                      </h3>
                      <p v-if="item.variant_name" class="text-lg sm:text-xl text-gray-600 dark:text-gray-400">
                        {{ item.variant_name }}
                      </p>
                    </div>
                  </div>
                  
                  <div v-if="item.category" class="mb-3">
                    <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-3 py-1 text-sm font-semibold text-gray-600 dark:text-gray-300 uppercase">
                      {{ item.category }}
                    </span>
                  </div>
                  
                  <!-- Orders breakdown -->
                  <div class="mt-3 space-y-1">
                    <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ t('app.views.kitchen.grouped.from_orders') }}:</p>
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="(orderInfo, idx) in item.orders" 
                        :key="idx"
                        class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium"
                      >
                        <span class="font-bold">{{ orderInfo.quantity }}x</span>
                        <span>{{ t('app.views.kitchen.order', { id: orderInfo.order_number || orderInfo.order_id }) }}</span>
                        <span v-if="orderInfo.table_number" class="text-xs">({{ t('app.views.kitchen.table_short', { number: orderInfo.table_number }) }})</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Orders View (All, Pending, Preparing) -->
      <div v-else>
        <div v-if="filteredOrders.length === 0" class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('app.views.kitchen.no_active') }}</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.kitchen.no_active_description') }}</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3">
        <div v-for="order in filteredOrders" :key="order.id" class="bg-white dark:bg-gray-900 dark:border-gray-700 border-gray-200 border-2 rounded-lg shadow-md overflow-hidden">
          <div class="p-2 sm:p-3 border-b border-gray-200 dark:border-gray-700">
            <div class="flex justify-between items-start gap-2">
              <div class="flex-1 min-w-0">
                <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white truncate">{{ t('app.views.kitchen.order', { id: order.order_number || order.id }) }}</h3>
                <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                  {{ formatTime(order.created_at) }}
                  <span v-if="order.table_number" class="ml-1 sm:ml-2">• {{ t('app.views.kitchen.table', { number: order.table_number }) }}</span>
                </p>
              </div>
              <span 
                class="flex-shrink-0 px-2 py-0.5 text-xs font-semibold rounded-full"
                :class="getStatusBadgeClass(order.status)"
              >
                {{ t(`app.status.${order.status}`) }}
              </span>
            </div>
            <div v-if="order.notes" class="mt-1.5 p-2 bg-yellow-50 dark:bg-yellow-900/20 text-sm sm:text-base text-yellow-700 dark:text-yellow-300 rounded font-medium">
              {{ order.notes }}
            </div>
          </div>

          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <!-- If order has persons, show grouped by person -->
            <template v-if="order.persons && order.persons.length > 0">
              <div v-for="person in order.persons" :key="person.id" class="border-l-4 border-indigo-500 pl-2 py-2">
                <h5 class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5 flex items-center gap-1">
                  <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  {{ person.name || $t('app.views.orders.modals.new_order.persons.person_label', { position: person.position }) }}
                </h5>
                
                <div class="space-y-1.5">
                  <div 
                    v-for="item in person.items" 
                    :key="item.id"
                    class="p-2 sm:p-3 rounded-md"
                    :class="{
                      'bg-yellow-50 dark:bg-yellow-900/20': item.status === 'pending',
                      'bg-blue-50 dark:bg-blue-900/20': item.status === 'preparing',
                      'bg-green-50 dark:bg-green-900/20': item.status === 'ready'
                    }"
                  >
                    <div class="flex flex-col gap-1.5">
                      <div class="flex items-center flex-wrap gap-1.5">
                        <span class="font-bold text-xl sm:text-2xl text-gray-900 dark:text-white">{{ item.quantity }}x</span>
                        <span class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{{ item.menu_item.name }}</span>
                        <span v-if="item.variant" class="text-sm sm:text-base text-gray-600 dark:text-gray-400">({{ item.variant.name }})</span>
                        
                        <span 
                          class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                          :class="getItemStatusBadgeClass(item.status)"
                        >
                          {{ t(`app.status.${item.status}`) }}
                        </span>
                        
                        <span class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-semibold ml-auto">
                          {{ getTimeElapsed(item.created_at) }}
                        </span>
                      </div>
                      
                      <!-- Category and Action Button on same line -->
                      <div class="flex items-center justify-between gap-2">
                        <div v-if="item.menu_item.category">
                          <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase">
                            {{ item.menu_item.category }}
                          </span>
                        </div>
                        
                        <!-- Item Action Button -->
                        <button
                          v-if="item.status === 'pending'"
                          @click="markItemPreparing(order, item)"
                          class="text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-shrink-0"
                        >
                          {{ t('app.views.kitchen.actions.start_preparing') }}
                        </button>
                        <button
                          v-if="item.status === 'preparing'"
                          @click="markItemReady(order, item)"
                          class="text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-md bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex-shrink-0"
                        >
                          {{ t('app.views.kitchen.actions.item_ready') }}
                        </button>
                      </div>
                      
                      <div v-if="item.special_instructions" class="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-sm sm:text-base font-semibold text-blue-700 dark:text-blue-300">
                        {{ item.special_instructions }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- Legacy view: show items without grouping -->
            <template v-else>
            <div 
              v-for="item in getPendingItems(order)" 
              :key="item.id"
              class="p-2 sm:p-3"
              :class="{
                'bg-yellow-50 dark:bg-yellow-900/20': item.status === 'pending',
                'bg-blue-50 dark:bg-blue-900/20': item.status === 'preparing',
                'bg-green-50 dark:bg-green-900/20': item.status === 'ready'
              }"
            >
              <div class="flex flex-col gap-1.5">
                <div class="flex items-center flex-wrap gap-1.5">
                  <span class="font-bold text-xl sm:text-2xl text-gray-900 dark:text-white">{{ item.quantity }}x</span>
                  <span class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{{ item.menu_item.name }}</span>
                  <span v-if="item.variant" class="text-sm sm:text-base text-gray-600 dark:text-gray-400">({{ item.variant.name }})</span>
                  
                  <!-- Item Status Badge -->
                  <span 
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="getItemStatusBadgeClass(item.status)"
                  >
                    {{ t(`app.status.${item.status}`) }}
                  </span>
                  
                  <span class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-semibold ml-auto">
                    {{ getTimeElapsed(item.created_at) }}
                  </span>
                </div>
                
                <!-- Category and Action Button on same line -->
                <div class="flex items-center justify-between gap-2">
                  <div v-if="item.menu_item.category">
                    <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase">
                      {{ item.menu_item.category }}
                    </span>
                  </div>
                  
                  <!-- Item Action Button -->
                  <button
                    v-if="item.status === 'pending'"
                    @click="markItemPreparing(order, item)"
                    class="text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-shrink-0"
                  >
                    {{ t('app.views.kitchen.actions.start_preparing') }}
                  </button>
                  <button
                    v-if="item.status === 'preparing'"
                    @click="markItemReady(order, item)"
                    class="text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-md bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex-shrink-0"
                  >
                    {{ t('app.views.kitchen.actions.item_ready') }}
                  </button>
                </div>
                
                <div v-if="item.special_instructions" class="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-sm sm:text-base font-semibold text-blue-700 dark:text-blue-300">
                   {{ item.special_instructions }}
                </div>
              </div>
            </div>
            </template>
          </div>

          <div class="p-2 sm:p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
            <!-- Bulk Actions for All Items -->
            <div class="space-y-1.5">
              <button
                v-if="hasPendingItems(order)"
                @click="startPreparingAllItems(order)"
                class="w-full bg-indigo-600 text-white py-2 sm:py-2.5 px-3 rounded-md hover:bg-indigo-700 active:bg-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 font-bold text-sm sm:text-base touch-manipulation"
              >
                {{ t('app.views.kitchen.actions.start_preparing_all') }}
              </button>
              <button
                v-if="hasPreparingItems(order)"
                @click="markAllItemsReady(order)"
                class="w-full bg-green-600 text-white py-2 sm:py-2.5 px-3 rounded-md hover:bg-green-700 active:bg-green-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 font-bold text-sm sm:text-base touch-manipulation"
              >
                {{ t('app.views.kitchen.actions.all_items_ready') }}
              </button>
            </div>
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
import { useLocalStorage } from '@vueuse/core';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import orderService from '@/services/orderService';
import type { Order, OrderItem } from '@/services/orderService';

const loading = ref(true);
const activeOrders = ref<Order[]>([]);
const selectedStatus = ref<'all' | 'pending' | 'preparing' | 'grouped'>('pending');
const selectedOrderType = useLocalStorage<'all' | 'dine_in' | 'takeaway' | 'delivery'>('kitchen-order-type-filter', 'all');
let refreshInterval: number | null = null;

const { t } = useI18n();

// Grouped items interface
interface GroupedItem {
  menu_item_id: number;
  menu_item_name: string;
  variant_id?: number;
  variant_name?: string;
  category?: string;
  total_quantity: number;
  orders: Array<{
    order_id: number;
    order_number?: number;
    table_number: number | null;
    quantity: number;
  }>;
}

// Computed: Group all active kitchen items by menu item and variant
// Also respects order type filter
const groupedItems = computed(() => {
  const groups = new Map<string, GroupedItem>();
  
  // Filter orders by order type first
  let ordersToGroup = activeOrders.value;
  if (selectedOrderType.value !== 'all') {
    ordersToGroup = ordersToGroup.filter(order => order.order_type === selectedOrderType.value);
  }
  
  // Iterate through filtered orders
  ordersToGroup.forEach(order => {
    const kitchenItems = getPendingItems(order);
    
    kitchenItems.forEach(item => {
      // Create unique key: menu_item_id + variant_id (if exists)
      const key = `${item.menu_item.id}_${item.variant?.id || 'no-variant'}`;
      
      if (!groups.has(key)) {
        groups.set(key, {
          menu_item_id: item.menu_item.id,
          menu_item_name: item.menu_item.name,
          variant_id: item.variant?.id,
          variant_name: item.variant?.name,
          category: item.menu_item.category,
          total_quantity: 0,
          orders: []
        });
      }
      
      const group = groups.get(key)!;
      group.total_quantity += item.quantity;
      group.orders.push({
        order_id: order.id,
        order_number: order.order_number,
        table_number: order.table_number,
        quantity: item.quantity
      });
    });
  });
  
  // Convert to array and sort by total quantity (descending)
  return Array.from(groups.values()).sort((a, b) => b.total_quantity - a.total_quantity);
});

// Status tabs with counts
// Only count orders that have visible items in kitchen
// Also respects order type filter
const statusTabs = computed(() => {
  let ordersWithVisibleItems = activeOrders.value.filter(order => {
    const visibleItems = getPendingItems(order);
    return visibleItems.length > 0;
  });
  
  // Apply order type filter to counts
  if (selectedOrderType.value !== 'all') {
    ordersWithVisibleItems = ordersWithVisibleItems.filter(order => 
      order.order_type === selectedOrderType.value
    );
  }
  
  const totalGroupedItems = groupedItems.value.length;
  
  return [
    {
      value: 'pending',
      label: t('app.views.kitchen.tabs.pending'),
      count: ordersWithVisibleItems.filter(o => o.status === 'pending').length
    },
    {
      value: 'preparing',
      label: t('app.views.kitchen.tabs.preparing'),
      count: ordersWithVisibleItems.filter(o => o.status === 'preparing').length
    },
    {
      value: 'grouped',
      label: t('app.views.kitchen.tabs.grouped'),
      count: totalGroupedItems
    }
  ];
});

// Order type tabs with counts
const orderTypeTabs = computed(() => {
  const ordersWithVisibleItems = activeOrders.value.filter(order => {
    const visibleItems = getPendingItems(order);
    return visibleItems.length > 0;
  });
  
  return [
    {
      value: 'all',
      label: t('app.views.kitchen.order_type_filter.all'),
      count: ordersWithVisibleItems.length
    },
    {
      value: 'dine_in',
      label: t('app.views.kitchen.order_type_filter.dine_in'),
      count: ordersWithVisibleItems.filter(o => o.order_type === 'dine_in').length
    },
    {
      value: 'takeaway',
      label: t('app.views.kitchen.order_type_filter.takeaway'),
      count: ordersWithVisibleItems.filter(o => o.order_type === 'takeaway').length
    },
    {
      value: 'delivery',
      label: t('app.views.kitchen.order_type_filter.delivery'),
      count: ordersWithVisibleItems.filter(o => o.order_type === 'delivery').length
    }
  ];
});

// Filtered orders based on selected status and order type
// Also filter out orders that have no visible items in kitchen
const filteredOrders = computed(() => {
  let orders = activeOrders.value;
  
  // Filter by status (skip filtering for grouped view)
  if (selectedStatus.value !== 'all' && selectedStatus.value !== 'grouped') {
    orders = orders.filter(order => order.status === selectedStatus.value);
  }
  
  // Filter by order type
  if (selectedOrderType.value !== 'all') {
    orders = orders.filter(order => order.order_type === selectedOrderType.value);
  }
  
  // Filter out orders with no kitchen-visible items
  orders = orders.filter(order => {
    const visibleItems = getPendingItems(order);
    return visibleItems.length > 0;
  });
  
  return orders;
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
// Also filter out items whose category is not visible in kitchen (e.g., beverages)
const getPendingItems = (order: Order) => {
  return order.items.filter(item => {
    const isActiveStatus = item.status === 'pending' || item.status === 'preparing';
    const isVisibleInKitchen = item.menu_item?.category_visible_in_kitchen !== false;
    return isActiveStatus && isVisibleInKitchen;
  });
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

/* Smooth scrolling for tabs on mobile */
.overflow-x-auto {
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.overflow-x-auto::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>
