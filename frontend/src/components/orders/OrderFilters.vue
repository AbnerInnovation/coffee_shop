<template>
  <div class="space-y-4">
    <!-- Status Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto overflow-y-hidden -mx-3 sm:mx-0">
      <nav class="flex -mb-px" aria-label="Tabs">
        <div class="flex space-x-4 sm:space-x-8 px-3 sm:px-0 min-w-max">
          <button 
            v-for="tab in tabs" 
            :key="tab.id" 
            @click="$emit('select-tab', tab.id as OrderStatus)" 
            :class="[
              'whitespace-nowrap border-b-2 py-3 sm:py-4 px-1 text-sm font-medium touch-manipulation',
              selectedStatus === tab.id
                ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-700 dark:hover:text-gray-100 hover:text-gray-700'
            ]"
          >
            <span class="inline-flex items-center">
              {{ $t('app.views.orders.tabs.' + tab.id) }}
              <span 
                v-if="tab.count > 0" 
                :class="[
                  selectedStatus === tab.id 
                    ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-300' 
                    : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-300',
                  'ml-2 py-0.5 px-2 rounded-full text-xs font-medium'
                ]"
              >
                {{ tab.count }}
              </span>
            </span>
          </button>
        </div>
      </nav>
    </div>

    <!-- Additional Filters -->
    <div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
      <!-- Payment Status Filter -->
      <div class="flex-1">
        <label for="payment-filter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('app.views.orders.filters.payment_status') || 'Estado de Pago' }}
        </label>
        <select
          id="payment-filter"
          :value="paymentFilter"
          @change="$emit('update:payment-filter', ($event.target as HTMLSelectElement).value as PaymentFilter)"
          class="block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
        >
          <option value="all">{{ $t('app.views.orders.filters.all_payments') || 'Todos' }}</option>
          <option value="paid">{{ $t('app.views.orders.filters.paid') || 'Pagados' }}</option>
          <option value="unpaid">{{ $t('app.views.orders.filters.unpaid') || 'No Pagados' }}</option>
        </select>
      </div>

      <!-- Order Type Filter -->
      <div class="flex-1">
        <label for="type-filter" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ $t('app.views.orders.filters.order_type') || 'Tipo de Orden' }}
        </label>
        <select
          id="type-filter"
          :value="orderType"
          @change="$emit('update:order-type', ($event.target as HTMLSelectElement).value as OrderTypeFilter)"
          class="block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
        >
          <option value="all">{{ $t('app.views.orders.filters.all_types') || 'Todos' }}</option>
          <option value="dine_in">{{ $t('app.views.orders.filters.dine_in') || 'Comer Aquí' }}</option>
          <option value="takeaway">{{ $t('app.views.orders.filters.takeaway') || 'Para Llevar' }}</option>
          <option value="delivery">{{ $t('app.views.orders.filters.delivery') || 'A Domicilio' }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
type OrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled' | 'all';
type PaymentFilter = 'all' | 'paid' | 'unpaid';
type OrderTypeFilter = 'all' | 'dine_in' | 'takeaway' | 'delivery';

interface Tab {
  id: string;
  count: number;
}

defineProps<{
  tabs: Tab[];
  selectedStatus: OrderStatus;
  paymentFilter: PaymentFilter;
  orderType: OrderTypeFilter;
}>();

defineEmits<{
  'select-tab': [tabId: OrderStatus];
  'update:payment-filter': [value: PaymentFilter];
  'update:order-type': [value: OrderTypeFilter];
}>();
</script>
