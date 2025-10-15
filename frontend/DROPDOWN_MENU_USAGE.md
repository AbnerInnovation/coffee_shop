# Dropdown Menu Components Usage Guide

## Overview
The reusable dropdown menu components provide a consistent way to add action menus throughout the application.

**Key Features:**
- ✅ **Singleton Pattern**: Only one dropdown can be open at a time across the entire app
- ✅ **High Z-Index**: z-index: 9999 ensures visibility above all elements
- ✅ **Auto-close**: Automatically closes when clicking outside or opening another dropdown
- ✅ **Dark Mode**: Full dark mode support
- ✅ **Accessible**: Proper ARIA attributes

## Components

### 1. DropdownMenu
Main container with the three-dots button.

**Props:**
- `modelValue` (boolean): Controls menu open/close state
- `buttonLabel` (string): Aria label for accessibility
- `width` ('sm' | 'md' | 'lg'): Menu width

### 2. DropdownMenuItem
Individual menu item with icon and variant styling.

**Props:**
- `icon` (Component): Heroicon component
- `variant` ('default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'): Color variant
- `disabled` (boolean): Disable the item

### 3. DropdownMenuDivider
Visual separator between menu sections.

## Example: Adding to Orders List

Here's how to add a dropdown menu to each order in OrdersView.vue:

```vue
<template>
  <!-- In the order list item -->
  <li v-for="order in filteredOrders" :key="order.id">
    <div class="p-4 sm:p-6 relative">
      <!-- Add dropdown menu in top-right corner -->
      <div class="absolute top-4 right-4" @click.stop>
        <DropdownMenu
          v-model="orderMenuStates[order.id]"
          button-label="Order actions"
          width="md"
        >
          <!-- View Details -->
          <DropdownMenuItem
            :icon="EyeIcon"
            variant="info"
            @click="viewOrderDetails(order)"
          >
            {{ t('app.views.orders.buttons.view') }}
          </DropdownMenuItem>
          
          <!-- Edit Order -->
          <DropdownMenuItem
            v-if="order.status !== 'completed' && order.status !== 'cancelled'"
            :icon="PencilIcon"
            variant="default"
            @click="editOrder(order)"
          >
            {{ t('app.actions.edit') }}
          </DropdownMenuItem>
          
          <DropdownMenuDivider />
          
          <!-- Status Actions -->
          <DropdownMenuItem
            v-if="order.status === 'pending'"
            :icon="PlayIcon"
            variant="primary"
            @click="updateOrderStatus(order.id, 'preparing')"
          >
            {{ t('app.views.orders.status_menu.mark_preparing') }}
          </DropdownMenuItem>
          
          <DropdownMenuItem
            v-if="order.status === 'preparing'"
            :icon="CheckIcon"
            variant="success"
            @click="updateOrderStatus(order.id, 'ready')"
          >
            {{ t('app.views.orders.status_menu.mark_ready') }}
          </DropdownMenuItem>
          
          <DropdownMenuItem
            v-if="order.status === 'ready'"
            :icon="CheckCircleIcon"
            variant="success"
            @click="updateOrderStatus(order.id, 'completed')"
          >
            {{ t('app.views.orders.status_menu.mark_completed') }}
          </DropdownMenuItem>
          
          <DropdownMenuDivider v-if="order.status !== 'cancelled' && order.status !== 'completed'" />
          
          <!-- Cancel Order -->
          <DropdownMenuItem
            v-if="order.status !== 'cancelled' && order.status !== 'completed'"
            :icon="XMarkIcon"
            variant="danger"
            @click="cancelOrder(order.id)"
          >
            {{ t('app.views.orders.status_menu.cancel_order') }}
          </DropdownMenuItem>
        </DropdownMenu>
      </div>
      
      <!-- Rest of order content -->
      <!-- ... -->
    </div>
  </li>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import {
  EyeIcon,
  PencilIcon,
  CheckIcon,
  CheckCircleIcon,
  XMarkIcon,
  PlayIcon
} from '@heroicons/vue/24/outline';

// Track menu states for each order
const orderMenuStates = ref<Record<number, boolean>>({});

// Close menu helper
const closeOrderMenu = (orderId: number) => {
  orderMenuStates.value[orderId] = false;
};

// Wrap existing functions to close menu
const viewOrderDetails = (order: Order) => {
  closeOrderMenu(order.id);
  // existing logic...
};

const editOrder = (order: Order) => {
  closeOrderMenu(order.id);
  // existing logic...
};

const updateOrderStatus = (orderId: number, status: string) => {
  closeOrderMenu(orderId);
  // existing logic...
};

const cancelOrder = (orderId: number) => {
  closeOrderMenu(orderId);
  // existing logic...
};
</script>
```

## Variant Colors

- **default**: Gray - For neutral actions (Edit, Settings)
- **primary**: Indigo - For primary actions (New, Create)
- **success**: Green - For positive actions (Complete, Approve)
- **warning**: Amber/Orange - For caution actions (Mark Occupied, Warning)
- **danger**: Red - For destructive actions (Delete, Cancel)
- **info**: Blue - For informational actions (View, Details)

## Best Practices

1. **Use v-model for menu state**: Track open/close state with a reactive object
2. **Close menu after action**: Always close the menu when an action is clicked
3. **Group related actions**: Use `DropdownMenuDivider` to separate action groups
4. **Conditional rendering**: Show/hide items based on state (e.g., order status)
5. **Accessibility**: Provide meaningful `button-label` for screen readers
6. **Stop propagation**: Add `@click.stop` to prevent parent click handlers

## Already Implemented

✅ **TablesView.vue** - Table management actions
- New Order / Edit Order
- Mark Available / Occupied
- Edit Table
- Delete Table
