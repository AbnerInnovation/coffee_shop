<template>
  <MainLayout>
    <div class="space-y-3 sm:space-y-6">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <XMarkIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{{ error }}</p>
            <button @click="() => fetchOrders()"
              class="mt-2 text-sm font-medium text-red-700 hover:text-red-600 focus:outline-none">
              {{ t('app.views.orders.try_again') }} <span aria-hidden="true">&rarr;</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="space-y-4 sm:space-y-6">
        <PageHeader :title="t('app.views.orders.title')"
          :subtitle="t('app.status.' + selectedStatus) + ' ' + t('app.views.orders.title').toLowerCase()">
          <template #actions>
            <button type="button" @click="openNewOrderModal"
              class="flex items-center justify-center rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 whitespace-nowrap">
              <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
              {{ t('app.views.orders.new_order') }}
            </button>
          </template>
        </PageHeader>
        <!-- Filters Component -->
        <OrderFilters :tabs="tabs" :selected-status="selectedStatus" :payment-filter="selectedPaymentFilter"
          :order-type="selectedOrderType" :table-filter="selectedTableFilter" :tables="tables"
          @select-tab="selectTab"
          @update:payment-filter="selectedPaymentFilter = $event" 
          @update:order-type="selectedOrderType = $event"
          @update:table-filter="selectedTableFilter = $event" />

        <!-- Order List Component -->
        <OrderList :orders="filteredOrders" @new-order="openNewOrderModal" @view="viewOrderDetails"
          @edit="openEditOrder" @complete="updateOrderStatus($event, 'completed')" @cancel="cancelOrder" />

        <!-- Order Details Modal -->
        <OrderDetails v-if="isOrderDetailsOpen && selectedOrder" :open="isOrderDetailsOpen" :order="selectedOrder"
          @close="closeOrderDetails" @status-update="handleStatusUpdate" @paymentCompleted="handlePaymentCompleted"
          @edit-order="openEditOrder" @openCashRegister="handleOpenCashRegister" />

        <!-- New Order Modal - only mount when needed -->
        <NewOrderModal v-if="isNewOrderModalOpen" :open="isNewOrderModalOpen" :mode="newOrderMode"
          :order-to-edit="newOrderMode === 'edit' ? selectedOrderForEdit : null"
          :table-id="newOrderMode === 'create' ? undefined : (selectedOrderForEdit?.table_id ?? undefined)"
          @close="closeNewOrderModal" @order-created="handleNewOrder" @order-updated="handleOrderUpdated" />
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import OrderFilters from '@/components/orders/OrderFilters.vue';
import OrderList from '@/components/orders/OrderList.vue';
import OrderDetails from '@/components/orders/OrderDetailsModal.vue';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import { PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { useOrderFilters, type PaymentFilter, type OrderTypeFilter, type TableFilter } from '@/composables/useOrderFilters';
import { useOrdersView } from '@/composables/useOrdersView';

/**
 * OrdersView - Main view for order management
 * 
 * Orchestrates order listing, filtering, creation, editing, and status management.
 * Uses composables for business logic separation following SOLID principles.
 */

// i18n
const { t } = useI18n();

// Business logic from composable
const {
  // State
  loading,
  error,
  orders,
  tables,
  selectedStatus,
  tabs,
  
  // Modal states
  isNewOrderModalOpen,
  newOrderMode,
  selectedOrderForEdit,
  isOrderDetailsOpen,
  selectedOrder,
  
  // Operations
  fetchOrders,
  fetchTables,
  selectTab,
  updateOrderStatus,
  cancelOrder,
  openNewOrderModal,
  closeNewOrderModal,
  openEditOrder,
  viewOrderDetails: viewOrderDetailsBase,
  closeOrderDetails,
  handleNewOrder,
  handleOrderUpdated,
  handleStatusUpdate,
  handlePaymentCompleted,
  handleOpenCashRegister,
  cleanup
} = useOrdersView();

// Local filter state (UI-only, not in composable)
const selectedPaymentFilter = ref<PaymentFilter>('all');
const selectedOrderType = ref<OrderTypeFilter>('all');
const selectedTableFilter = ref<TableFilter>('all');

// Use order filters composable for client-side filtering
const { filteredOrders } = useOrderFilters(
  orders,
  selectedStatus,
  selectedPaymentFilter,
  selectedOrderType,
  selectedTableFilter
);

/**
 * Wrapper for viewOrderDetails to handle nextTick
 * Required because composable can't use nextTick directly
 */
const viewOrderDetails = (order: any) => {
  viewOrderDetailsBase(order);
  nextTick(() => {
    // Ensure modal is open after DOM update
  });
};

// Initialize component
onMounted(() => {
  fetchOrders();
  fetchTables();
});

// Cleanup on unmount
onUnmounted(() => {
  cleanup();
});
</script>
