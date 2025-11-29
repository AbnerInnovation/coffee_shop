<template>
  <div class="space-y-3 sm:space-y-4">
    <!-- Order Type -->
    <div>
      <label for="order-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ $t('app.views.orders.modals.new_order.order_type') }}
      </label>
      <select 
        id="order-type" 
        :value="modelValue.type"
        @change="updateType"
        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
      >
        <option value="Dine-in">{{ $t('app.views.orders.modals.new_order.dine_in') }}</option>
        <option value="Takeaway">{{ $t('app.views.orders.modals.new_order.takeaway') }}</option>
        <option value="Delivery">{{ $t('app.views.orders.modals.new_order.delivery') }}</option>
      </select>
    </div>

    <!-- Table Selection (Dine-in) -->
    <div v-if="modelValue.type === 'Dine-in'">
      <label for="table" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ $t('app.views.orders.modals.new_order.table') }}
      </label>
      <select 
        id="table" 
        :value="modelValue.tableId || ''"
        @change="updateTableId"
        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
        :disabled="!!loading"
        style="max-width: 100%; width: 100%;"
      >
        <option v-if="loading" value="" disabled>...</option>
        <option v-else-if="error && tables.length === 0" value="" disabled>Error</option>
        <option v-else-if="tables.length === 0 && !allowDineInWithoutTable" value="" disabled>Sin mesas</option>
        <option v-if="allowDineInWithoutTable" value="">{{ $t('app.views.orders.modals.new_order.no_table') }}</option>
        <option v-for="table in sortedTables" :key="table.id" :value="table.id">
          Mesa {{ table.number }}
        </option>
      </select>
    </div>

    <!-- Customer Name/Address (Takeaway/Delivery) -->
    <div v-else>
      <label for="customer-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ modelValue.type === 'Delivery' 
          ? $t('app.views.orders.modals.new_order.delivery_address') 
          : $t('app.views.orders.modals.new_order.customer_name') 
        }}
      </label>
      <input 
        id="customer-name" 
        :value="modelValue.customerName"
        @input="updateCustomerName"
        type="text"
        class="mt-1 p-3 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        :placeholder="modelValue.type === 'Delivery' 
          ? $t('app.views.orders.modals.new_order.enter_delivery_address') 
          : $t('app.views.orders.modals.new_order.enter_customer_name')" 
      />
    </div>

    <!-- Notes -->
    <div>
      <label for="notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ $t('app.views.orders.modals.new_order.order_notes') }}
      </label>
      <textarea 
        id="notes" 
        :value="modelValue.notes"
        @input="updateNotes"
        rows="3"
        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
        :placeholder="$t('app.views.orders.modals.new_order.notes_placeholder')" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { OrderFormData } from '@/composables/useOrderForm';

interface Table {
  id: number;
  number: number;
  capacity: number;
}

interface Props {
  modelValue: any; // Accept any form type to avoid type conflicts
  tables: Table[];
  loading: boolean | string | null;
  error: boolean | string | null;
  allowDineInWithoutTable?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:modelValue': [value: OrderFormData];
}>();

// Sort tables by number in ascending order
const sortedTables = computed(() => {
  return [...props.tables].sort((a, b) => a.number - b.number);
});

const updateType = (e: Event) => {
  const target = e.target as HTMLSelectElement;
  emit('update:modelValue', { ...props.modelValue, type: target.value as any });
};

const updateTableId = (e: Event) => {
  const target = e.target as HTMLSelectElement;
  const val = target.value;
  // Handle empty string (No Table) as null
  emit('update:modelValue', { ...props.modelValue, tableId: val ? Number(val) : null });
};

const updateCustomerName = (e: Event) => {
  const target = e.target as HTMLInputElement;
  emit('update:modelValue', { ...props.modelValue, customerName: target.value });
};

const updateNotes = (e: Event) => {
  const target = e.target as HTMLTextAreaElement;
  emit('update:modelValue', { ...props.modelValue, notes: target.value });
};
</script>
