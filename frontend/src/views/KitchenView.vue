<template>
  <MainLayout>
    <div class="kitchen-view space-y-4 sm:space-y-6">
      <PageHeader :title="t('app.views.kitchen.title')"
        :subtitle="t('app.views.kitchen.last_updated', { time: new Date().toLocaleTimeString() })" />

      <!-- Filters -->
      <KitchenFilters v-model:selectedStatus="selectedStatus" v-model:selectedOrderType="selectedOrderType"
        :statusTabs="statusTabs" :orderTypeTabs="orderTypeTabs" />

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>

      <!-- Grouped View -->
      <KitchenGroupedView v-else-if="selectedStatus === 'grouped'" :groupedItems="groupedItems" />

      <!-- Orders View (All, Pending, Preparing) -->
      <div v-else>
        <!-- Empty State -->
        <div v-if="filteredOrders.length === 0"
          class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"
            aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.kitchen.no_active') }}
          </h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ t('app.views.kitchen.no_active_description') }}
          </p>
        </div>

        <!-- Orders Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3">
          <KitchenOrderCard v-for="order in filteredOrders" :key="order.id" :order="order"
            @start-preparing="handleMarkItemPreparing" @mark-ready="handleMarkItemReady"
            @start-preparing-all="handleStartPreparingAll" @mark-all-ready="handleMarkAllReady" />
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useLocalStorage } from '@vueuse/core';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import type { Order, OrderItem } from '@/services/orderService';
import { useKitchenOrders } from '@/composables/useKitchenOrders';
import { useKitchenFilters, type KitchenStatusFilter, type OrderTypeFilter } from '@/composables/useKitchenFilters';
import { useKitchenItems } from '@/composables/useKitchenItems';
import KitchenFilters from '@/components/kitchen/KitchenFilters.vue';
import KitchenOrderCard from '@/components/kitchen/KitchenOrderCard.vue';
import KitchenGroupedView from '@/components/kitchen/KitchenGroupedView.vue';

const { t } = useI18n();

// State
const selectedStatus = ref<KitchenStatusFilter>('pending');
const selectedOrderType = useLocalStorage<OrderTypeFilter>('kitchen-order-type-filter', 'all');

// Composables
const { loading, activeOrders, fetchActiveOrders } = useKitchenOrders();
const { filteredOrders, groupedItems, statusTabs, orderTypeTabs } = useKitchenFilters(
  activeOrders,
  selectedStatus,
  selectedOrderType,
  t
);
const { markItemPreparing, markItemReady, startPreparingAllItems, markAllItemsReady } = useKitchenItems(fetchActiveOrders);

// Event handlers - Delegate to composable methods
const handleMarkItemPreparing = (order: Order, item: OrderItem) => {
  markItemPreparing(order, item);
};

const handleMarkItemReady = (order: Order, item: OrderItem) => {
  markItemReady(order, item);
};

const handleStartPreparingAll = (order: Order) => {
  startPreparingAllItems(order);
};

const handleMarkAllReady = (order: Order) => {
  markAllItemsReady(order);
};
</script>

<style scoped>
.kitchen-view {
  max-width: 1800px;
  margin: 0 auto;
}
</style>
