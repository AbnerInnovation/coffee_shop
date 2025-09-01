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

    <!-- Tables Grid -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div 
        v-for="table in tables" 
        :key="table.id"
        class="relative rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200"
        :class="{
          'ring-2 ring-offset-2 ring-indigo-500': selectedTableId === table.id
        }"
        @click="selectTable(table.id)"
      >
        <!-- Table Status Badge -->
        <div 
          class="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium"
          :class="getStatusBadgeClass(table.status)"
        >
          {{ table.status }}
        </div>

        <div class="p-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">Table {{ table.number }}</h3>
            <span class="text-sm text-gray-500">Seats: {{ table.capacity }}</span>
          </div>
          
          <div v-if="table.currentOrder" class="mt-2">
            <div class="text-sm text-gray-500">
              Order #{{ table.currentOrder.id }}
              <span class="mx-1">•</span>
              <span>${{ table.currentOrder.total.toFixed(2) }}</span>
            </div>
            <div class="mt-1 text-xs text-gray-400">
              {{ formatTimeAgo(table.currentOrder.createdAt) }}
            </div>
          </div>
          
          <div v-else class="mt-2 text-sm text-gray-500">
            No active order
          </div>
          
          <div class="mt-4 flex space-x-2">
            <button
              v-if="table.status === 'Available'"
              type="button"
              class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              @click.stop="startNewOrder(table.id)"
            >
              New Order
            </button>
            <button
              v-else
              type="button"
              class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              @click.stop="viewOrder(table.currentOrder.id)"
            >
              View Order
            </button>
            <button
              v-if="table.status !== 'Available'"
              type="button"
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              @click.stop="checkoutTable(table.id)"
            >
              Checkout
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Details Sidebar -->
    <TableDetailsSidebar 
      :open="isSidebarOpen" 
      :table="selectedTable"
      @close="closeSidebar"
      @checkout="handleCheckout"
      @start-order="handleStartOrder"
    />
    
    <!-- Add/Edit Table Modal -->
    <TableFormModal
      :open="isTableModalOpen"
      :table="editingTable"
      @close="closeTableModal"
      @save="handleSaveTable"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { PlusIcon } from '@heroicons/vue/24/outline';
import TableDetailsSidebar from '@/components/tables/TableDetailsSidebar.vue';
import TableFormModal from '@/components/tables/TableFormModal.vue';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();

// Mock data - replace with API calls
const tables = ref([
  {
    id: '1',
    number: '01',
    capacity: 4,
    status: 'Occupied',
    location: 'Window',
    currentOrder: {
      id: '1001',
      total: 42.50,
      items: [
        { name: 'Cappuccino', quantity: 2, price: 4.50 },
        { name: 'Avocado Toast', quantity: 1, price: 12.00 },
        { name: 'Orange Juice', quantity: 1, price: 5.50 }
      ],
      createdAt: new Date(Date.now() - 30 * 60 * 1000) // 30 minutes ago
    }
  },
  {
    id: '2',
    number: '02',
    capacity: 2,
    status: 'Available',
    location: 'Bar',
    currentOrder: null
  },
  // Add more mock tables as needed
]);

const selectedTableId = ref(null);
const isSidebarOpen = ref(false);
const isTableModalOpen = ref(false);
const editingTable = ref(null);

const selectedTable = computed(() => {
  if (!selectedTableId.value) return null;
  return tables.value.find(table => table.id === selectedTableId.value);
});

function getStatusBadgeClass(status) {
  const statusClasses = {
    'Available': 'bg-green-100 text-green-800',
    'Occupied': 'bg-yellow-100 text-yellow-800',
    'Reserved': 'bg-blue-100 text-blue-800',
    'Out of Service': 'bg-red-100 text-red-800',
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

function formatTimeAgo(date) {
  const now = new Date();
  const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

function selectTable(tableId) {
  selectedTableId.value = tableId;
  isSidebarOpen.value = true;
}

function closeSidebar() {
  isSidebarOpen.value = false;
  // Don't reset selectedTableId to keep it highlighted
}

function startNewOrder(tableId) {
  // In a real app, this would open a modal to create a new order
  const table = tables.value.find(t => t.id === tableId);
  if (table) {
    table.status = 'Occupied';
    table.currentOrder = {
      id: Math.floor(1000 + Math.random() * 9000).toString(),
      total: 0,
      items: [],
      createdAt: new Date()
    };
    showSuccess(`Started new order for Table ${table.number}`);
    // In a real app, you would navigate to the order page
  }
}

function viewOrder(orderId) {
  // In a real app, you would navigate to the order details page
  console.log('Viewing order:', orderId);
}

async function checkoutTable(tableId) {
  const confirmed = await confirm({
    title: 'Checkout Table',
    message: 'Are you sure you want to checkout this table? This will mark the table as available.',
    confirmText: 'Yes, checkout',
    cancelText: 'No, keep it',
    confirmClass: 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
  });
  
  if (confirmed) {
    try {
      const table = tables.value.find(t => t.id === tableId);
      if (table) {
        table.status = 'Available';
        table.currentOrder = null;
        showSuccess(`Table ${table.number} has been checked out`);
      }
    } catch (error) {
      console.error('Error checking out table:', error);
      showError('Failed to checkout table');
    }
  }
}

function handleCheckout(tableId) {
  checkoutTable(tableId);
  closeSidebar();
}

function handleStartOrder(tableId) {
  startNewOrder(tableId);
  closeSidebar();
}

function openAddTableModal() {
  editingTable.value = null;
  isTableModalOpen.value = true;
}

function openEditTableModal(table) {
  editingTable.value = { ...table };
  isTableModalOpen.value = true;
}

function closeTableModal() {
  isTableModalOpen.value = false;
  editingTable.value = null;
}

function handleSaveTable(tableData) {
  try {
    if (tableData.id) {
      // Update existing table
      const index = tables.value.findIndex(t => t.id === tableData.id);
      if (index !== -1) {
        tables.value[index] = { ...tables.value[index], ...tableData };
        showSuccess('Table updated successfully');
      }
    } else {
      // Add new table
      tables.value.push({
        ...tableData,
        id: Math.random().toString(36).substr(2, 9),
        status: 'Available',
        currentOrder: null
      });
      showSuccess('Table added successfully');
    }
    closeTableModal();
  } catch (error) {
    console.error('Error saving table:', error);
    showError('Failed to save table');
  }
}

// In a real app, you would fetch tables from an API
onMounted(() => {
  // fetchTables();
});
</script>
