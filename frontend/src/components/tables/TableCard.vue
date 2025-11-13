<template>
  <div 
    :data-dropdown-container="`table-${table.id}`"
    class="relative rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer"
    :class="{
      'ring-2 ring-offset-2 ring-indigo-500': isSelected,
      'border-l-4 border-red-500': table.is_occupied,
      'border-l-4 border-green-500': !table.is_occupied
    }"
    @click="$emit('select', table)"
  >
    <!-- Three Dots Menu -->
    <div class="absolute top-2 right-2 z-30" @click.stop>
      <DropdownMenu
        :model-value="isMenuOpen"
        @update:model-value="$emit('update:menuOpen', $event)"
        :id="`table-${table.id}`"
        button-label="Table actions"
        width="md"
      >
        <!-- Order Actions -->
        <DropdownMenuItem
          v-if="canCreateOrders && !hasOpenOrder"
          :icon="PlusIcon"
          variant="primary"
          @click="$emit('new-order', table)"
        >
          {{ t('app.views.orders.new_order') || 'New Order' }}
        </DropdownMenuItem>
        
        <template v-else-if="canCreateOrders && hasOpenOrder">
          <DropdownMenuItem
            :icon="ShoppingBagIcon"
            variant="warning"
            @click="$emit('edit-order', table)"
          >
            {{ t('app.views.orders.edit_order') || 'Edit Order' }}
          </DropdownMenuItem>
          <DropdownMenuItem
            :icon="PlusIcon"
            variant="info"
            @click="$emit('add-items', table)"
          >
            {{ t('app.views.orders.add_items') || 'Add Items' }}
          </DropdownMenuItem>
          <DropdownMenuItem
            :icon="DocumentTextIcon"
            variant="default"
            @click="$emit('view-bill', table)"
          >
            {{ t('app.views.tables.view_bill') || 'Ver cuenta' }}
          </DropdownMenuItem>
        </template>
        
        <DropdownMenuDivider v-if="canCreateOrders || canManageTables" />
        
        <!-- Table Actions -->
        <DropdownMenuItem
          v-if="canManageTables"
          :icon="table.is_occupied ? CheckCircleIcon : XCircleIconOutline"
          :variant="table.is_occupied ? 'success' : 'warning'"
          @click="$emit('toggle-occupancy', table)"
        >
          {{ table.is_occupied ? t('app.views.tables.mark_available') : t('app.views.tables.mark_occupied') }}
        </DropdownMenuItem>
        <DropdownMenuItem
          v-if="canManageTables"
          :icon="PencilIcon"
          variant="default"
          @click="$emit('edit', table)"
        >
          {{ t('app.views.tables.edit') }}
        </DropdownMenuItem>
        <DropdownMenuItem
          v-if="canManageTables"
          :icon="TrashIcon"
          variant="danger"
          @click="$emit('delete', table)"
        >
          {{ t('app.actions.delete') }}
        </DropdownMenuItem>
      </DropdownMenu>
    </div>

    <!-- Table Status Badge -->
    <div 
      class="absolute top-2 right-10 px-2 py-0.5 rounded-full text-xs font-medium"
      :class="table.is_occupied ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200' : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'"
    >
      {{ table.is_occupied ? t('app.views.tables.occupied') : t('app.views.tables.available') }}
    </div>

    <!-- Table Info -->
    <div class="p-3">
      <div class="flex items-start justify-between pr-14">
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">
            {{ t('app.views.tables.table_number_header', { number: table.number }) }}
          </h3>
          <span class="text-xs text-gray-500 dark:text-gray-400">
            {{ t('app.views.tables.seats', { count: table.capacity }) }}
          </span>
        </div>
      </div>
      
      <div class="mt-2">
        <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
          {{ t('app.views.tables.location', { location: translatedLocation }) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon, 
  CheckCircleIcon, 
  XCircleIcon as XCircleIconOutline, 
  ShoppingBagIcon, 
  DocumentTextIcon 
} from '@heroicons/vue/24/outline';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import type { Table } from '@/services/tableService';

interface Props {
  table: Table;
  isSelected?: boolean;
  hasOpenOrder?: boolean;
  canManageTables?: boolean;
  canCreateOrders?: boolean;
  isMenuOpen?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isSelected: false,
  hasOpenOrder: false,
  canManageTables: false,
  canCreateOrders: false,
  isMenuOpen: false
});

defineEmits<{
  'select': [table: Table];
  'new-order': [table: Table];
  'edit-order': [table: Table];
  'add-items': [table: Table];
  'view-bill': [table: Table];
  'toggle-occupancy': [table: Table];
  'edit': [table: Table];
  'delete': [table: Table];
  'update:menuOpen': [value: boolean];
}>();

const { t } = useI18n();

// Translate location from English to current locale
const translatedLocation = computed(() => {
  const locationMap: Record<string, string> = {
    'Inside': t('app.views.tables.modal.fields.location_inside'),
    'Patio': t('app.views.tables.modal.fields.location_patio'),
    'Bar': t('app.views.tables.modal.fields.location_bar')
  };
  return locationMap[props.table.location] || props.table.location;
});
</script>
