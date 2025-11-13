<template>
  <MainLayout>
    <div class="tables-view space-y-4 sm:space-y-6">
      <!-- Page Header -->
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

      <!-- States: Loading, Error, Empty -->
      <TableStates
        :loading="loading"
        :error="error"
        :is-empty="tables.length === 0 && !loading && !error"
        :can-manage-tables="canManageTables"
        @add-table="openAddTableModal"
      />

      <!-- Tables Grid -->
      <div 
        v-if="!loading && !error && tables.length > 0"
        class="grid grid-cols-1 gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
      >
        <TableCard
          v-for="table in tables"
          :key="table.id"
          :table="table"
          :is-selected="selectedTableId === table.id"
          :has-open-order="hasOpenOrder(table.id)"
          :can-manage-tables="canManageTables"
          :can-create-orders="canCreateOrders"
          :is-menu-open="menuStates[table.id]"
          @select="handleSelectTable"
          @new-order="handleNewOrder"
          @edit-order="handleEditOrder"
          @add-items="handleAddItems"
          @view-bill="handleViewBill"
          @toggle-occupancy="handleToggleOccupancy"
          @edit="handleEditTable"
          @delete="handleDeleteTable"
          @update:menu-open="menuStates[table.id] = $event"
        />
      </div>

      <!-- Add/Edit Table Modal -->
      <TableFormModal
        :is-open="showTableModal"
        :table="editingTableId ? tableToEdit : {}"
        :is-editing="editingTableId !== null"
        @close="closeTableModal"
        @save="handleSaveTable"
      />

      <!-- New Order Modal -->
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

      <!-- Order Details Modal (View Bill) -->
      <OrderDetailsModal
        v-if="showOrderDetailsModal && selectedOrderForDetails"
        :open="showOrderDetailsModal"
        :order="selectedOrderForDetails"
        @close="showOrderDetailsModal = false"
        @status-update="handleOrderStatusUpdate"
        @paymentCompleted="handlePaymentCompleted"
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
import { useTables } from '@/composables/useTables';
import { useTableOrders } from '@/composables/useTableOrders';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import TableCard from '@/components/tables/TableCard.vue';
import TableStates from '@/components/tables/TableStates.vue';
import TableFormModal from '@/components/tables/TableFormModal.vue';
import { PlusIcon } from '@heroicons/vue/24/outline';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import AddItemsModal from '@/components/orders/AddItemsModal.vue';
import OrderDetailsModal from '@/components/orders/OrderDetailsModal.vue';
import LimitReachedModal from '@/components/subscription/LimitReachedModal.vue';
import BaseButton from '@/components/ui/BaseButton.vue';
import type { Table } from '@/services/tableService';

const { t } = useI18n();
const { canManageTables, canCreateOrders } = usePermissions();

// Composables
const {
  tables,
  loading,
  error,
  selectedTableId,
  fetchTables,
  createTable,
  updateTable,
  deleteTable,
  toggleOccupancy,
  selectTable,
  clearError
} = useTables();

const {
  hasOpenOrder,
  refreshOpenOrders,
  getOpenOrderForTable,
  getOrderDetails
} = useTableOrders();

// Table form state
const showTableModal = ref(false);
const editingTableId = ref<number | null>(null);
const tableToEdit = ref<Table | {}>({});

// Menu states for dropdown
const menuStates = ref<Record<number, boolean>>({});

// Order modal state
const showOrderModal = ref(false);
const selectedTableForOrder = ref<Table | null>(null);
const orderModalMode = ref<'create' | 'edit'>('create');
const orderToEdit = ref<any>(null);

// Add items modal state
const showAddItemsModal = ref(false);
const selectedTableForAddItems = ref<Table | null>(null);
const selectedOrderId = ref<number | null>(null);

// Order details modal state (View Bill)
const showOrderDetailsModal = ref(false);
const selectedOrderForDetails = ref<any>(null);

// Limit reached modal state
const showLimitModal = ref(false);
const limitMessage = ref('');
const currentUsage = ref<number | null>(null);
const maxLimit = ref<number | null>(null);

// Table modal handlers
const openAddTableModal = () => {
  tableToEdit.value = {};
  editingTableId.value = null;
  showTableModal.value = true;
};

const closeTableModal = () => {
  showTableModal.value = false;
  editingTableId.value = null;
  tableToEdit.value = {};
  clearError();
};

const handleSaveTable = async (tableData: any) => {
  let result;
  if (editingTableId.value !== null) {
    result = await updateTable(editingTableId.value, tableData);
  } else {
    result = await createTable(tableData);
  }

  if (result.success) {
    closeTableModal();
  } else if (result.isLimitError) {
    // Show limit modal
    limitMessage.value = result.message || '';
    currentUsage.value = result.currentUsage ?? null;
    maxLimit.value = result.maxLimit ?? null;
    showLimitModal.value = true;
    closeTableModal();
  }
  // Error is already set in composable
};

// Table card event handlers
const handleSelectTable = (table: Table) => {
  selectTable(table.id);
};

const handleEditTable = (table: Table) => {
  tableToEdit.value = table;
  editingTableId.value = table.id;
  showTableModal.value = true;
};

const handleDeleteTable = async (table: Table) => {
  if (!confirm(t('app.views.tables.confirm_delete', { number: table.number }) || `Are you sure you want to delete Table #${table.number}?`)) {
    return;
  }

  await deleteTable(table.id);
};

const handleToggleOccupancy = async (table: Table) => {
  await toggleOccupancy(table.id, table.is_occupied);
};

// Order-related handlers
const handleNewOrder = (table: Table) => {
  selectedTableForOrder.value = table;
  orderModalMode.value = 'create';
  orderToEdit.value = null;
  showOrderModal.value = true;
};

const handleEditOrder = async (table: Table) => {
  try {
    const openOrder = await getOpenOrderForTable(table.id);
    
    if (openOrder) {
      selectedTableForOrder.value = table;
      orderModalMode.value = 'edit';
      orderToEdit.value = openOrder;
      showOrderModal.value = true;
    } else {
      // This shouldn't happen as the button only shows when there's an open order
      console.warn('No open order found for table:', table.id);
    }
  } catch (err) {
    console.error('Error fetching order for table:', err);
  }
};

const handleAddItems = async (table: Table) => {
  try {
    const openOrder = await getOpenOrderForTable(table.id);
    
    if (openOrder) {
      selectedTableForAddItems.value = table;
      selectedOrderId.value = openOrder.id;
      showAddItemsModal.value = true;
    } else {
      console.warn('No open order found for table:', table.id);
    }
  } catch (err) {
    console.error('Error fetching order for table:', err);
  }
};

const handleViewBill = async (table: Table) => {
  try {
    const openOrder = await getOpenOrderForTable(table.id);
    
    if (openOrder) {
      // Fetch complete order details with calculated totals
      const fullOrderDetails = await getOrderDetails(openOrder.id);
      selectedOrderForDetails.value = fullOrderDetails;
      showOrderDetailsModal.value = true;
    } else {
      console.warn('No open order found for table:', table.id);
    }
  } catch (err) {
    console.error('Error fetching order for table:', err);
  }
};

const closeOrderModal = () => {
  showOrderModal.value = false;
  orderModalMode.value = 'create';
  orderToEdit.value = null;
};

const handleOrderCreated = () => {
  fetchTables();
  refreshOpenOrders();
};

const handleOrderStatusUpdate = () => {
  fetchTables();
  refreshOpenOrders();
};

const handlePaymentCompleted = () => {
  fetchTables();
  refreshOpenOrders();
  showOrderDetailsModal.value = false;
};

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
