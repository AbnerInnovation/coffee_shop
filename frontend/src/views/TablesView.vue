<template>
  <MainLayout>
    <div class="tables-view space-y-4 sm:space-y-6">
    <PageHeader
      :title="t('app.views.tables.title')"
      :subtitle="t('app.views.tables.subtitle')"
    >
      <template #actions>
        <BaseButton
          v-if="canManageTables"
          variant="primary"
          @click="openAddTableModal"
        >
          <template #icon>
            <PlusIcon class="h-5 w-5" aria-hidden="true" />
          </template>
          {{ t('app.views.tables.add_table') }}
        </BaseButton>
      </template>
    </PageHeader>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ t('app.views.tables.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-4 mb-4 rounded-r-lg">
      <div class="flex">
        <div class="flex-shrink-0">
          <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
        </div>
        <div class="ml-3">
          <p class="text-sm text-red-700 dark:text-red-300">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="tables.length === 0" class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">{{ t('app.views.tables.no_tables') }}</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.tables.no_tables_description') }}</p>
      <div v-if="canManageTables" class="mt-6">
        <BaseButton variant="primary" @click="openAddTableModal">
          <template #icon>
            <PlusIcon class="h-5 w-5" aria-hidden="true" />
          </template>
          {{ t('app.views.tables.add_table') }}
        </BaseButton>
      </div>
    </div>

    <!-- Tables Grid -->
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div 
        v-for="table in tables" 
        :key="table.id"
        :data-dropdown-container="`table-${table.id}`"
        class="relative rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm hover:shadow-md transition-shadow duration-200"
        :class="{
          'ring-2 ring-offset-2 ring-indigo-500': selectedTableId === table.id,
          'border-l-4 border-red-500': table.is_occupied,
          'border-l-4 border-green-500': !table.is_occupied
        }"
        @click="selectTable(table)"
      >
        <!-- Three Dots Menu -->
        <div class="absolute top-2 right-2 z-30" @click.stop>
          <DropdownMenu
            v-model="menuStates[table.id]"
            :id="`table-${table.id}`"
            button-label="Table actions"
            width="md"
          >
            <!-- Order Actions (only for users who can create orders) -->
            <DropdownMenuItem
              v-if="canCreateOrders && !hasOpenOrder(table.id)"
              :icon="PlusIcon"
              variant="primary"
              @click="openOrderModalFromMenu(table)"
            >
              {{ t('app.views.orders.new_order') || 'New Order' }}
            </DropdownMenuItem>
            <template v-else-if="canCreateOrders && hasOpenOrder(table.id)">
              <DropdownMenuItem
                :icon="ShoppingBagIcon"
                variant="warning"
                @click="goToEditOrderFromMenu(table)"
              >
                {{ t('app.views.orders.edit_order') || 'Edit Order' }}
              </DropdownMenuItem>
              <DropdownMenuItem
                :icon="PlusIcon"
                variant="info"
                @click="openAddItemsModal(table)"
              >
                {{ t('app.views.orders.add_items') || 'Add Items' }}
              </DropdownMenuItem>
            </template>
            
            <DropdownMenuDivider v-if="canCreateOrders || canManageTables" />
            
            <!-- Table Actions (only for users who can manage tables) -->
            <DropdownMenuItem
              v-if="canManageTables"
              :icon="table.is_occupied ? CheckCircleIcon : XCircleIconOutline"
              :variant="table.is_occupied ? 'success' : 'warning'"
              @click="toggleOccupancyFromMenu(table)"
            >
              {{ table.is_occupied ? t('app.views.tables.mark_available') : t('app.views.tables.mark_occupied') }}
            </DropdownMenuItem>
            <DropdownMenuItem
              v-if="canManageTables"
              :icon="PencilIcon"
              variant="default"
              @click="editTableFromMenu(table)"
            >
              {{ t('app.views.tables.edit') }}
            </DropdownMenuItem>
            <DropdownMenuItem
              v-if="canManageTables"
              :icon="TrashIcon"
              variant="danger"
              @click="confirmDeleteTable(table)"
            >
              {{ t('app.actions.delete') }}
            </DropdownMenuItem>
          </DropdownMenu>
        </div>

        <!-- Table Status Badge -->
        <div 
          class="absolute top-2 right-12 px-2 py-1 rounded-full text-xs font-medium"
          :class="table.is_occupied ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200' : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'"
        >
          {{ table.is_occupied ? t('app.views.tables.occupied') : t('app.views.tables.available') }}
        </div>

        <div class="p-4 pb-3">
          <div class="flex items-start justify-between pr-16 sm:pr-20">
            <div>
              <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-gray-100">{{ t('app.views.tables.table_number_header', { number: table.number }) }}</h3>
              <span class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.tables.seats', { count: table.capacity }) }}</span>
            </div>
          </div>
          
          <div class="mt-3">
            <div class="text-sm text-gray-600 dark:text-gray-300">
              {{ t('app.views.tables.location', { location: translateLocation(table.location) }) }}
            </div>
            <div class="mt-1 text-xs text-gray-400 dark:text-gray-500">
              {{ t('app.views.tables.last_updated', { time: formatTimeAgo(table.updated_at) }) }}
            </div>
          </div>
          
          <!-- Removed order buttons - now in menu -->
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
                class="mt-1 block px-3 py-2 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
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
                class="mt-1 block px-3 py-2 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:border-gray-700 dark:text-white"
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
              <BaseButton
                type="button"
                variant="secondary"
                size="sm"
                @click="closeModal"
              >
                {{ t('app.views.tables.modal.actions.cancel') }}
              </BaseButton>
              <BaseButton
                type="submit"
                variant="primary"
                size="sm"
              >
                {{ editingTable ? t('app.views.tables.modal.actions.submit_update') : t('app.views.tables.modal.actions.submit_add') }}
              </BaseButton>
            </div>
          </div>
        </form>
      </div>
    </div>
    <!-- New Order Modal (same used in Orders view) - only mount when needed -->
    <NewOrderModal
      v-if="showOrderModal"
      :open="showOrderModal"
      :table-id="selectedTableForOrder ? selectedTableForOrder.id : null"
      :mode="orderModalMode"
      :order-to-edit="orderToEdit"
      @close="closeOrderModal"
      @order-created="handleOrderCreated"
    />

    <!-- Add Items Modal -->
    <AddItemsModal
      v-if="showAddItemsModal"
      :open="showAddItemsModal"
      :order-id="selectedOrderId!"
      :table-number="selectedTableForAddItems?.number ?? 0"
      @close="showAddItemsModal = false"
      @success="handleItemsAdded"
    />

    <!-- Limit Reached Modal -->
    <LimitReachedModal
      :is-open="showLimitModal"
      :message="limitMessage"
      :current-usage="currentUsage ?? undefined"
      :max-limit="maxLimit ?? undefined"
      resource-type="tables"
      @close="showLimitModal = false"
    />
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import { PlusIcon, XMarkIcon, XCircleIcon, PencilIcon, TrashIcon, CheckCircleIcon, XCircleIcon as XCircleIconOutline, ShoppingBagIcon } from '@heroicons/vue/24/outline';
import tableService from '@/services/tableService';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import AddItemsModal from '@/components/orders/AddItemsModal.vue';
import LimitReachedModal from '@/components/subscription/LimitReachedModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import { formatDistanceToNow } from 'date-fns';
import orderService from '@/services/orderService';
import { useRouter } from 'vue-router';

import type { Table } from '@/services/tableService';

const { t } = useI18n();
const router = useRouter();
const { canManageTables, canCreateOrders } = usePermissions();
const tables = ref<Table[]>([]);
const loading = ref(false);
const error = ref('');
const selectedTableId = ref<number | null>(null);
const showTableModal = ref(false);
const editingTable = ref<number | null>(null);
const menuStates = ref<Record<number, boolean>>({});

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

// Track open orders by table_id
const openOrderTableIds = ref<Set<number>>(new Set());

const refreshOpenOrders = async () => {
  try {
    // Fetch active orders (pending, preparing, ready) and not paid
    const all = await orderService.getActiveOrders();
    const active = (Array.isArray(all) ? all : []).filter(o => o && o.table_id && o.status !== 'completed' && o.status !== 'cancelled' && !o.is_paid);
    openOrderTableIds.value = new Set(active.map(o => o.table_id).filter((id): id is number => id !== null));
  } catch (e) {
    console.warn('Failed to fetch open orders for tables view:', e);
  }
};

const hasOpenOrder = (tableId: number) => openOrderTableIds.value.has(tableId);

// Translate location from English to current locale
const translateLocation = (location: string) => {
  const locationMap: Record<string, string> = {
    'Inside': t('app.views.tables.modal.fields.location_inside'),
    'Patio': t('app.views.tables.modal.fields.location_patio'),
    'Bar': t('app.views.tables.modal.fields.location_bar')
  };
  return locationMap[location] || location;
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
  } catch (err: any) {
    console.error('Error saving table:', err);
    
    // Handle subscription limit errors (403)
    if (err?.response?.status === 403) {
      const errorDetail = err.response?.data?.detail || err.response?.data?.error?.message || 'Límite de suscripción alcanzado. Por favor mejora tu plan.';
      
      // Extract usage info if available
      limitMessage.value = errorDetail;
      
      // Try to parse usage from error message (e.g., "Maximum 10 tables allowed")
      const match = errorDetail.match(/Maximum (\d+)/);
      if (match) {
        maxLimit.value = parseInt(match[1]);
        currentUsage.value = tables.value.length;
      }
      
      showLimitModal.value = true;
      closeModal();
    } else {
      error.value = err?.response?.data?.detail || 
                   err?.response?.data?.error?.message ||
                   `Failed to ${editingTable.value !== null ? 'update' : 'create'} table. Please try again.`;
    }
  }
};

// Select table
const selectTable = (table) => {
  selectedTableId.value = table.id;
  // Here you could add logic to show table details or orders
};

// Order modal state
const showOrderModal = ref(false);
const selectedTableForOrder = ref<Table | null>(null);
const orderModalMode = ref<'create' | 'edit'>('create');
const orderToEdit = ref<any>(null);

// Add items modal state
const showAddItemsModal = ref(false);
const selectedTableForAddItems = ref<Table | null>(null);
const selectedOrderId = ref<number | null>(null);

// Limit reached modal state
const showLimitModal = ref(false);
const limitMessage = ref('');
const currentUsage = ref<number | null>(null);
const maxLimit = ref<number | null>(null);

// Open order modal for a table (NewOrderModal)
const openOrderModal = (table) => {
  selectedTableForOrder.value = table;
  orderModalMode.value = 'create';
  orderToEdit.value = null;
  showOrderModal.value = true;
};

// Close order modal and reset state
const closeOrderModal = () => {
  showOrderModal.value = false;
  orderModalMode.value = 'create';
  orderToEdit.value = null;
};

// Handle order created event
const handleOrderCreated = (order) => {
  // You might want to update the table status or show a notification
  fetchTables(); // Refresh tables to show updated status
  refreshOpenOrders();
};

// Open edit order modal
const goToEditOrder = async (table: Table) => {
  try {
    // Get the open order for this table
    const orders = await orderService.getActiveOrders(undefined, table.id);
    const openOrder = orders.find(o => o.table_id === table.id && o.status !== 'completed' && o.status !== 'cancelled' && !o.is_paid);
    
    if (openOrder) {
      selectedTableForOrder.value = table;
      orderModalMode.value = 'edit';
      orderToEdit.value = openOrder;
      showOrderModal.value = true;
    } else {
      error.value = t('app.views.orders.errors.no_open_order') || 'No open order found for this table.';
    }
  } catch (err) {
    console.error('Error fetching order for table:', err);
    error.value = t('app.views.orders.errors.fetch_failed') || 'Failed to fetch order. Please try again.';
  }
};

// Close menu helper
const closeMenu = (tableId: number) => {
  menuStates.value[tableId] = false;
};

// Toggle occupancy from menu
const toggleOccupancyFromMenu = async (table: Table) => {
  closeMenu(table.id);
  await toggleOccupancy(table);
};

// Open order modal from menu
const openOrderModalFromMenu = (table: Table) => {
  closeMenu(table.id);
  openOrderModal(table);
};

// Go to edit order from menu
const goToEditOrderFromMenu = async (table: Table) => {
  closeMenu(table.id);
  await goToEditOrder(table);
};

// Edit table from menu
const editTableFromMenu = (table: Table) => {
  closeMenu(table.id);
  formData.value = {
    number: table.number,
    capacity: table.capacity,
    location: table.location,
    is_occupied: table.is_occupied
  };
  editingTable.value = table.id;
  showTableModal.value = true;
};

// Confirm and delete table
const confirmDeleteTable = async (table: Table) => {
  closeMenu(table.id);
  
  if (!confirm(t('app.views.tables.confirm_delete', { number: table.number }) || `Are you sure you want to delete Table #${table.number}?`)) {
    return;
  }
  
  try {
    await tableService.deleteTable(table.id);
    await fetchTables();
  } catch (err) {
    console.error('Error deleting table:', err);
    error.value = t('app.views.tables.errors.delete_failed') || 'Failed to delete table. Please try again.';
  }
};

// Open add items modal
const openAddItemsModal = async (table: Table) => {
  closeMenu(table.id);
  
  try {
    // Get the open order for this table
    const orders = await orderService.getActiveOrders(undefined, table.id);
    const openOrder = orders.find(o => o.table_id === table.id && o.status !== 'completed' && o.status !== 'cancelled' && !o.is_paid);
    
    if (openOrder) {
      selectedTableForAddItems.value = table;
      selectedOrderId.value = openOrder.id;
      showAddItemsModal.value = true;
    } else {
      error.value = t('app.views.orders.errors.no_open_order') || 'No open order found for this table.';
    }
  } catch (err) {
    console.error('Error fetching order for table:', err);
    error.value = t('app.views.orders.errors.fetch_failed') || 'Failed to fetch order. Please try again.';
  }
};

// Handle items added successfully
const handleItemsAdded = () => {
  fetchTables();
  refreshOpenOrders();
};

// Initialize component
onMounted(() => {
  fetchTables();
  refreshOpenOrders();
});
</script>
