<template>
  <div class="tables-view space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('app.views.tables.title') }}</h2>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.tables.subtitle') }}</p>
      </div>
      <div class="flex items-center space-x-3">
        <button
          type="button"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          @click="openAddTableModal"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          {{ t('app.views.tables.add_table') }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ t('app.views.tables.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
      <div class="flex">
        <div class="flex-shrink-0">
          <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Tables Grid -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div 
        v-for="table in tables" 
        :key="table.id"
        class="relative rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200"
        :class="{
          'ring-2 ring-offset-2 ring-indigo-500': selectedTableId === table.id,
          'border-l-4 border-red-500': table.is_occupied,
          'border-l-4 border-green-500': !table.is_occupied
        }"
        @click="selectTable(table)"
      >
        <!-- Table Status Badge -->
        <div 
          class="absolute bottom-4 right-4 px-2 py-1 rounded-full text-xs font-medium"
          :class="table.is_occupied ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
        >
          {{ table.is_occupied ? t('app.views.tables.occupied') : t('app.views.tables.available') }}
        </div>

        <div class="p-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">{{ t('app.views.tables.table_number_header', { number: table.number }) }}</h3>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.tables.seats', { count: table.capacity }) }}</span>
          </div>
          
          <div class="mt-2">
            <div class="text-sm text-gray-600 dark:text-gray-300">
              {{ t('app.views.tables.location', { location: table.location }) }}
            </div>
            <div class="mt-1 text-xs text-gray-400 dark:text-gray-500">
              {{ t('app.views.tables.last_updated', { time: formatTimeAgo(table.updated_at) }) }}
            </div>
          </div>
          
          <div class="mt-4 flex space-x-2">
              <button
                type="button"
                class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white"
                :class="table.is_occupied ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
                @click.stop="toggleOccupancy(table)"
              >
                {{ table.is_occupied ? t('app.views.tables.mark_available') : t('app.views.tables.mark_occupied') }}
              </button>
            <button
              type="button"
              class="inline-flex items-center px-3 py-1.5 border text-xs font-medium rounded shadow-sm text-gray-700 bg-white hover:bg-gray-50 border-gray-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 dark:hover:bg-gray-700"
              @click.stop="editTable(table)"
            >
              {{ t('app.views.tables.edit') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Table Modal -->
    <div v-if="showTableModal" class="fixed inset-0 bg-gray-900/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-800">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            {{ editingTable ? t('app.views.tables.modal.edit_title') : t('app.views.tables.modal.add_title') }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
            <span class="sr-only">{{ t('app.views.tables.modal.close') }}</span>
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        
        <form @submit.prevent="saveTable">
          <div class="space-y-4">
            <div>
              <label for="table-number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.tables.modal.fields.table_number') }}</label>
              <input
                id="table-number"
                :value="formData.number"
                @input="formData.number = Number(($event.target as HTMLInputElement).value)"
                type="number"
                min="1"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              >
            </div>
            
            <div>
              <label for="table-capacity" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.tables.modal.fields.capacity') }}</label>
              <input
                id="table-capacity"
                :value="formData.capacity"
                @input="formData.capacity = Number(($event.target as HTMLInputElement).value)"
                type="number"
                min="1"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              >
            </div>
            
            <div>
              <label for="table-location" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.tables.modal.fields.location') }}</label>
              <select
                id="table-location"
                v-model="formData.location"
                required
                class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
              >
                <option value="Inside">{{ t('app.views.tables.modal.fields.location_inside') }}</option>
                <option value="Patio">{{ t('app.views.tables.modal.fields.location_patio') }}</option>
                <option value="Bar">{{ t('app.views.tables.modal.fields.location_bar') }}</option>
              </select>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 dark:hover:bg-gray-700 dark:focus:ring-offset-gray-900"
              >
                {{ t('app.views.tables.modal.actions.cancel') }}
              </button>
              <button
                type="submit"
                class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                {{ editingTable ? t('app.views.tables.modal.actions.submit_update') : t('app.views.tables.modal.actions.submit_add') }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
    <!-- Order Modal -->
    <div v-if="showOrderModal && selectedTableForOrder">
      <OrderModal
        :table-id="selectedTableForOrder.id"
        :table-number="selectedTableForOrder.number"
        @close="showOrderModal = false"
        @order-created="handleOrderCreated"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { PlusIcon, XMarkIcon, XCircleIcon } from '@heroicons/vue/24/outline';
import tableService from '@/services/tableService';
import OrderModal from '@/components/orders/OrderModal.vue';
import { formatDistanceToNow } from 'date-fns';

import type { Table } from '@/services/tableService';

const { t } = useI18n();
const tables = ref<Table[]>([]);
const loading = ref(false);
const error = ref('');
const selectedTableId = ref<number | null>(null);
const showTableModal = ref(false);
const editingTable = ref<number | null>(null);

interface TableFormData {
  number: number;
  capacity: number;
  location: string;
  is_occupied: boolean;
}

const formData = ref<TableFormData>({
  number: 1, // Number type
  capacity: 2, // Number type
  location: 'Inside',
  is_occupied: false
});

// Fetch tables from API
const fetchTables = async () => {
  try {
    loading.value = true;
    tables.value = await tableService.getTables();
    error.value = '';
  } catch (err) {
    console.error('Error fetching tables:', err);
    error.value = 'Failed to load tables. Please try again.';
  } finally {
    loading.value = false;
  }
};

// Format time ago
const formatTimeAgo = (dateString) => {
  if (!dateString) return '';
  return formatDistanceToNow(new Date(dateString), { addSuffix: true });
};

// Toggle table occupancy
const toggleOccupancy = async (table) => {
  try {
    await tableService.updateTableOccupancy(table.id, !table.is_occupied);
    await fetchTables();
  } catch (err) {
    console.error('Error updating table status:', err);
    error.value = 'Failed to update table status. Please try again.';
  }
};

// Open modal to add new table
const openAddTableModal = () => {
  formData.value = {
    number: 1,
    capacity: 2,
    location: 'Inside',
    is_occupied: false
  };
  editingTable.value = null;
  showTableModal.value = true;
};

// Open modal to edit table
const editTable = (table: Table) => {
  formData.value = {
    number: table.number,
    capacity: table.capacity,
    location: table.location,
    is_occupied: table.is_occupied
  };
  editingTable.value = table.id;
  showTableModal.value = true;
};

// Close modal
const closeModal = () => {
  showTableModal.value = false;
};

// Save table (create or update)
const saveTable = async () => {
  try {
    const tableData = {
      ...formData.value,
      number: Number(formData.value.number),
      capacity: Number(formData.value.capacity)
    };
    
    if (editingTable.value !== null) {
      await tableService.updateTable(editingTable.value, tableData);
    } else {
      await tableService.createTable(tableData);
    }
    await fetchTables();
    closeModal();
  } catch (err) {
    console.error('Error saving table:', err);
    error.value = `Failed to ${editingTable.value !== null ? 'update' : 'create'} table. Please try again.`;
  }
};

// Select table
const selectTable = (table) => {
  selectedTableId.value = table.id;
  // Here you could add logic to show table details or orders
  console.log('Selected table:', table);
};

// Order modal state
const showOrderModal = ref(false);
const selectedTableForOrder = ref<Table | null>(null);

// Open order modal for a table
const openOrderModal = (table) => {
  selectedTableForOrder.value = table;
  showOrderModal.value = true;
};

// Handle order created event
const handleOrderCreated = (order) => {
  console.log('Order created:', order);
  // You might want to update the table status or show a notification
  fetchTables(); // Refresh tables to show updated status
};

// Initialize component
onMounted(() => {
  fetchTables();
});
</script>
