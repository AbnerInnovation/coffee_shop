<template>
  <li 
    :data-dropdown-container="`order-${order.id}`" 
    class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
  >
    <div class="p-3 sm:p-6 border-b border-gray-100 dark:border-gray-700 relative">
      <!-- Three Dots Menu -->
      <div class="absolute top-3 right-3 sm:top-4 sm:right-4" @click.stop>
        <DropdownMenu
          :id="`order-${order.id}`"
          button-label="Order actions"
          width="md"
        >
          <!-- View Details -->
          <DropdownMenuItem
            :icon="EyeIcon"
            variant="info"
            @click="$emit('view', order)"
          >
            {{ $t('app.views.orders.buttons.view') }}
          </DropdownMenuItem>
          
          <!-- Edit Order -->
          <DropdownMenuItem
            v-if="order.status !== 'completed' && order.status !== 'cancelled' && !order.is_paid"
            :icon="PencilIcon"
            variant="default"
            @click="$emit('edit', order)"
          >
            {{ $t('app.actions.edit') }}
          </DropdownMenuItem>
          
          <!-- Status Actions -->
          <DropdownMenuDivider v-if="order.status === 'ready' || canCancel" />
          
          <DropdownMenuItem
            v-if="order.status === 'ready'"
            :icon="CheckCircleIcon"
            variant="success"
            @click="$emit('complete', order.id)"
          >
            {{ $t('app.views.orders.buttons.complete') }}
          </DropdownMenuItem>
          
          <DropdownMenuDivider v-if="order.status === 'ready' && canCancel" />
          
          <!-- Cancel Order -->
          <DropdownMenuItem
            v-if="canCancel"
            :icon="XMarkIcon"
            variant="danger"
            @click="$emit('cancel', order.id)"
          >
            {{ $t('app.views.orders.buttons.cancel') }}
          </DropdownMenuItem>
        </DropdownMenu>
      </div>
      
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0 pr-10 sm:pr-12">
        <div class="flex-1 min-w-0">
          <!-- Order Info -->
          <div class="flex items-center flex-wrap gap-1.5 sm:gap-2">
            <p class="text-sm font-semibold text-indigo-600 dark:text-indigo-400">
              #{{ order.order_number || order.id }}
            </p>
            <span 
              class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
              :class="statusBadgeClass"
            >
              {{ $t('app.status.' + order.status) }}
            </span>
            <span
              class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
              :class="order.is_paid 
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' 
                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'"
            >
              {{ order.is_paid ? $t('app.views.orders.payment.paid') : $t('app.views.orders.payment.pending') }}
            </span>
            <span
              v-if="orderType"
              class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200"
            >
              {{ orderType }}
            </span>
          </div>
          
          <div class="mt-1.5 sm:mt-2 flex flex-wrap gap-x-3 sm:gap-x-4 gap-y-1 sm:gap-y-2">
            <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <RectangleGroupIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400 dark:text-gray-500" />
              <span class="truncate">{{ order.table }}</span>
            </div>
            <!-- Show customer name for takeaway/delivery orders -->
            <div 
              v-if="showCustomerName" 
              class="flex items-center text-sm text-gray-500 dark:text-gray-400"
            >
              <UserIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400 dark:text-gray-500" />
              <span class="truncate">{{ order.customer_name || 'Cliente' }}</span>
            </div>
            <div class="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <ClockIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400 dark:text-gray-500" />
              <span>{{ formattedTime }}</span>
            </div>
          </div>
        </div>
        
        <div class="mt-2 sm:mt-0 sm:ml-4 flex-shrink-0">
          <p class="text-lg sm:text-lg font-semibold text-gray-900 dark:text-white">
            ${{ order.total.toFixed(2) }}
          </p>
        </div>
      </div>

      <!-- Order Items Summary -->
      <div class="mt-2 sm:mt-3 pt-2 sm:pt-3 border-t border-gray-100 dark:border-gray-700">
        <div class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
          <span class="font-medium text-gray-900 dark:text-gray-100">
            {{ order.items.length }} {{ order.items.length === 1 ? $t('app.views.orders.summary.item') : $t('app.views.orders.summary.items') }}
          </span>
          <span class="hidden sm:inline mx-1">•</span>
          <span class="truncate">{{ itemsSummary }}</span>
        </div>
      </div>
    </div>
  </li>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import { 
  EyeIcon, 
  PencilIcon, 
  CheckCircleIcon, 
  XMarkIcon,
  RectangleGroupIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/vue/24/outline';
import { getStatusBadgeClass, formatTime, getOrderItemsSummary, getOrderTypeLabel, canCancelOrder } from '@/utils/orderHelpers';
import type { OrderWithLocalFields } from '@/utils/orderHelpers';
import { canCancelOrders } from '@/utils/permissions';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();

const props = defineProps<{
  order: OrderWithLocalFields;
}>();

defineEmits<{
  view: [order: OrderWithLocalFields];
  edit: [order: OrderWithLocalFields];
  complete: [orderId: number];
  cancel: [orderId: number];
}>();

const statusBadgeClass = computed(() => getStatusBadgeClass(props.order.status));
const formattedTime = computed(() => formatTime(props.order.createdAt));
const itemsSummary = computed(() => getOrderItemsSummary(props.order.items));
const canCancel = computed(() => {
  // Only admin/sysadmin can cancel orders AND order must be cancellable
  return canCancelOrders(authStore.user) && canCancelOrder(props.order);
});
const orderType = computed(() => {
  const type = (props.order as any).order_type;
  return type ? getOrderTypeLabel(type) : null;
});
const showCustomerName = computed(() => {
  const type = (props.order as any).order_type;
  // Show customer name for takeaway and delivery orders
  return type === 'takeaway' || type === 'delivery';
});
</script>
