<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Tables</h2>
        <p class="mt-1 text-sm text-gray-500">Manage tables and their status</p>
      </div>
      <div class="flex items-center space-x-3">
        <button
          type="button"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          @click="openAddTableModal"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          Add Table
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
      <p class="mt-2 text-sm text-gray-600">Loading tables...</p>
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
        class="relative rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200"
        :class="{
          'ring-2 ring-offset-2 ring-indigo-500': selectedTableId === table.id,
          'border-l-4 border-red-500': table.is_occupied,
          'border-l-4 border-green-500': !table.is_occupied
        }"
        @click="selectTable(table)"
      >
        <!-- Table Status Badge -->
        <div 
          class="absolute bottom-2 right-2 px-2 py-1 rounded-full text-xs font-medium"
          :class="table.is_occupied ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'"
        >
          {{ table.is_occupied ? 'Occupied' : 'Available' }}
        </div>

        <div class="p-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Table #{{ table.number }}</h3>
            <span class="text-sm text-gray-500">Seats: {{ table.capacity }}</span>
          </div>
          
          <div class="mt-2">
            <div class="text-sm text-gray-600">
              Location: {{ table.location }}
            </div>
            <div class="mt-1 text-xs text-gray-400">
              Last updated: {{ formatTimeAgo(table.updated_at) }}
            </div>
          </div>
          
          <div class="mt-4 flex space-x-2">
            <div class="grid grid-cols-2 gap-2 mt-2">
              <button
                type="button"
                class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white"
                :class="table.is_occupied ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'"
                @click.stop="toggleOccupancy(table)"
              >
                {{ table.is_occupied ? 'Available' : 'Occupied' }}
              </button>
              <button
                type="button"
                class="inline-flex items-center justify-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                @click.stop="openOrderModal(table)"
              >
                New Order
              </button>
            </div>
            <button
              type="button"
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded shadow-sm text-gray-700 bg-white hover:bg-gray-50"
              @click.stop="editTable(table)"
            >
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Table Modal -->
    <div v-if="showTableModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ editingTable ? 'Edit Table' : 'Add New Table' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
            <span class="sr-only">Close</span>
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        
        <form @submit.prevent="saveTable">
          <div class="space-y-4">
            <div>
              <label for="table-number" class="block text-sm font-medium text-gray-700">Table Number</label>
              <input
                id="table-number"
                v-model="formData.number"
                type="number"
                min="1"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
            </div>
            
            <div>
              <label for="table-capacity" class="block text-sm font-medium text-gray-700">Capacity</label>
              <input
                id="table-capacity"
                v-model="formData.capacity"
                type="number"
                min="1"
                required
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              >
            </div>
            
            <div>
              <label for="table-location" class="block text-sm font-medium text-gray-700">Location</label>
              <select
                id="table-location"
                v-model="formData.location"
                required
                class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              >
                <option value="Inside">Inside</option>
                <option value="Patio">Patio</option>
                <option value="Bar">Bar</option>
              </select>
            </div>
            
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                {{ editingTable ? 'Update' : 'Add' }} Table
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
  
  <!-- Order Modal -->
  <OrderModal
    v-if="showOrderModal && selectedTableForOrder"
    :table-id="selectedTableForOrder.id"
    :table-number="selectedTableForOrder.number"
    @close="showOrderModal = false"
    @order-created="handleOrderCreated"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { PlusIcon, XMarkIcon, XCircleIcon } from '@heroicons/vue/24/outline';
import tableService from '@/services/tableService';
import OrderModal from '@/components/orders/OrderModal.vue';
import { formatDistanceToNow } from 'date-fns';

const tables = ref([]);
const loading = ref(false);
const error = ref('');
const selectedTableId = ref(null);
const showTableModal = ref(false);
const editingTable = ref(null);

const formData = ref({
  number: '',
  capacity: 2,
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
    number: '',
    capacity: 2,
    location: 'Inside',
    is_occupied: false
  };
  editingTable.value = null;
  showTableModal.value = true;
};

// Open modal to edit table
const editTable = (table) => {
  formData.value = {
    number: table.number,
    capacity: table.capacity,
    location: table.location,
    is_occupied: table.is_occupied
  };
  editingTable.value = table;
  showTableModal.value = true;
};

// Close modal
const closeModal = () => {
  showTableModal.value = false;
};

// Save table (create or update)
const saveTable = async () => {
  try {
    if (editingTable.value) {
      await tableService.updateTable(editingTable.value.id, formData.value);
    } else {
      await tableService.createTable(formData.value);
    }
    await fetchTables();
    closeModal();
  } catch (err) {
    console.error('Error saving table:', err);
    error.value = `Failed to ${editingTable.value ? 'update' : 'create'} table. Please try again.`;
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
const selectedTableForOrder = ref(null);

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
