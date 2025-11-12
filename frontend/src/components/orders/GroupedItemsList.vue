<template>
  <div class="space-y-2">
    <!-- Empty State -->
    <div v-if="groupedItems.length === 0" 
      class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ emptyMessage }}
      </p>
    </div>

    <!-- Grouped Items -->
    <div 
      v-for="group in groupedItems" 
      :key="group.fingerprint"
      class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-sm"
    >
      <!-- Item Header -->
      <div class="flex items-start justify-between gap-3">
        <!-- Item Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
              {{ group.name }}
            </h4>
            <span v-if="group.variant_name" 
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
              {{ group.variant_name }}
            </span>
          </div>
          <p v-if="group.category" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {{ group.category }}
          </p>
        </div>

        <!-- Price & Quantity -->
        <div class="flex flex-col items-end gap-1">
          <div class="flex items-center gap-2">
            <!-- Quantity Controls (if editable) -->
            <div v-if="editable && !isLocked(group)" class="flex items-center gap-1">
              <button
                @click="$emit('decrease', group)"
                class="w-7 h-7 flex items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 active:scale-95 transition-all"
                :disabled="group.quantity <= 1"
                :class="{ 'opacity-50 cursor-not-allowed': group.quantity <= 1 }"
              >
                <MinusIcon class="h-4 w-4" />
              </button>
              
              <span class="min-w-[2rem] text-center font-semibold text-gray-900 dark:text-gray-100">
                {{ group.quantity }}
              </span>
              
              <button
                @click="$emit('increase', group)"
                class="w-7 h-7 flex items-center justify-center rounded-md bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-200 dark:hover:bg-indigo-900/50 active:scale-95 transition-all"
              >
                <PlusIcon class="h-4 w-4" />
              </button>
            </div>

            <!-- Quantity Display (if not editable) -->
            <span v-else class="text-sm font-medium text-gray-600 dark:text-gray-400">
              {{ group.quantity }}x
            </span>
          </div>

          <!-- Total Price -->
          <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
            ${{ (group.price * group.quantity).toFixed(2) }}
          </span>
          
          <!-- Unit Price (if quantity > 1) -->
          <span v-if="group.quantity > 1" class="text-xs text-gray-500 dark:text-gray-400">
            ${{ group.price.toFixed(2) }} c/u
          </span>
        </div>
      </div>

      <!-- Special Instructions -->
      <div v-if="group.hasCustomizations" class="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
        <div class="flex items-start gap-2">
          <SparklesIcon class="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
          <div class="flex-1 space-y-0.5">
            <p 
              v-for="(line, index) in getFormattedInstructions(group)" 
              :key="index"
              class="text-xs text-gray-600 dark:text-gray-400"
            >
              {{ line }}
            </p>
          </div>
        </div>
      </div>

      <!-- Remove Button (if editable) -->
      <div v-if="editable && !isLocked(group)" class="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
        <button
          @click="$emit('remove', group)"
          class="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
        >
          <TrashIcon class="h-4 w-4" />
          {{ $t('app.actions.remove') }}
        </button>
      </div>

      <!-- Status Badge (if exists) -->
      <div v-if="group.status && showStatus" class="mt-2">
        <span :class="getStatusClass(group.status)">
          {{ getStatusLabel(group.status) }}
        </span>
      </div>
    </div>

    <!-- Summary (if showSummary) -->
    <div v-if="showSummary && groupedItems.length > 0" 
      class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-3">
      <div class="flex justify-between items-center">
        <div class="text-sm text-indigo-700 dark:text-indigo-300">
          <span class="font-medium">{{ totalItemCount }}</span>
          {{ totalItemCount === 1 ? 'item' : 'items' }}
          <span v-if="groupCount !== totalItemCount" class="text-xs">
            ({{ groupCount }} {{ groupCount === 1 ? 'grupo' : 'grupos' }})
          </span>
        </div>
        <span class="text-base font-bold text-indigo-900 dark:text-indigo-100">
          ${{ totalPrice.toFixed(2) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MinusIcon, PlusIcon, TrashIcon, SparklesIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import type { GroupedOrderItem } from '@/utils/orderItemGrouping';

interface Props {
  groupedItems: GroupedOrderItem[];
  totalItemCount: number;
  groupCount: number;
  totalPrice: number;
  getFormattedInstructions: (group: GroupedOrderItem) => string[];
  editable?: boolean;
  showSummary?: boolean;
  showStatus?: boolean;
  isLocked?: (group: GroupedOrderItem) => boolean;
  emptyMessage?: string;
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  showSummary: true,
  showStatus: false,
  isLocked: () => false,
  emptyMessage: 'Sin items agregados aún'
});

defineEmits<{
  (e: 'increase', group: GroupedOrderItem): void;
  (e: 'decrease', group: GroupedOrderItem): void;
  (e: 'remove', group: GroupedOrderItem): void;
}>();

const { t } = useI18n();

const getStatusClass = (status: string) => {
  const baseClasses = 'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium';
  const statusClasses: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    preparing: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    ready: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    served: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  };
  return `${baseClasses} ${statusClasses[status] || statusClasses.pending}`;
};

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: t('app.status.pending'),
    preparing: t('app.status.preparing'),
    ready: t('app.status.ready'),
    served: t('app.status.served')
  };
  return labels[status] || status;
};
</script>
