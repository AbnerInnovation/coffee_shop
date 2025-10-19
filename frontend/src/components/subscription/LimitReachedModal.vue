<template>
  <TransitionRoot :show="isOpen" as="template">
    <Dialog as="div" class="relative z-50" @close="closeModal">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 shadow-xl transition-all">
              <!-- Icon -->
              <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                <ExclamationTriangleIcon class="h-6 w-6 text-yellow-600 dark:text-yellow-500" />
              </div>

              <!-- Title -->
              <DialogTitle class="mt-4 text-center text-lg font-semibold text-gray-900 dark:text-white">
                {{ t('app.subscription.limit_reached_title') }}
              </DialogTitle>

              <!-- Message -->
              <div class="mt-3">
                <p class="text-sm text-gray-600 dark:text-gray-400 text-center">
                  {{ message }}
                </p>

                <!-- Current Usage -->
                <div v-if="currentUsage && maxLimit" class="mt-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-700 dark:text-gray-300">{{ t('app.subscription.current_usage') }}:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">
                      {{ currentUsage }} / {{ maxLimit === -1 ? '∞' : maxLimit }}
                    </span>
                  </div>
                  <div class="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div 
                      class="bg-red-600 h-2 rounded-full" 
                      :style="{ width: maxLimit === -1 ? '0%' : `${Math.min((currentUsage / maxLimit) * 100, 100)}%` }"
                    ></div>
                  </div>
                </div>

                <!-- Current Plan -->
                <div v-if="currentPlan" class="mt-3 text-center">
                  <p class="text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.subscription.your_current_plan') }}: 
                    <span class="font-semibold text-gray-700 dark:text-gray-300">{{ currentPlan }}</span>
                  </p>
                </div>
              </div>

              <!-- Actions -->
              <div class="mt-6 grid grid-cols-1 gap-3">
                <!-- Upgrade Plan Button -->
                <button
                  type="button"
                  class="inline-flex justify-center items-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2"
                  @click="handleUpgrade"
                >
                  <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  {{ t('app.subscription.upgrade_plan') }}
                </button>

                <!-- View Add-ons Button (if applicable) -->
                <button
                  v-if="showAddonsOption"
                  type="button"
                  class="inline-flex justify-center items-center rounded-lg bg-gray-100 dark:bg-gray-700 px-4 py-2.5 text-sm font-semibold text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  @click="handleViewAddons"
                >
                  <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  {{ t('app.subscription.view_addons') }}
                </button>

                <!-- Cancel Button -->
                <button
                  type="button"
                  class="inline-flex justify-center rounded-lg bg-white dark:bg-gray-800 px-4 py-2.5 text-sm font-semibold text-gray-900 dark:text-gray-300 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
                  @click="closeModal"
                >
                  {{ t('app.actions.cancel') }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';

const { t } = useI18n();
const router = useRouter();

const props = defineProps<{
  isOpen: boolean;
  message: string;
  currentUsage?: number;
  maxLimit?: number;
  currentPlan?: string;
  limitType?: 'menu_items' | 'tables' | 'categories' | 'users';
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

// Show add-ons option for menu items, tables, and categories
const showAddonsOption = ref(
  props.limitType === 'menu_items' || 
  props.limitType === 'tables'
);

const closeModal = () => {
  emit('close');
};

const handleUpgrade = () => {
  closeModal();
  router.push('/subscription');
};

const handleViewAddons = () => {
  closeModal();
  router.push('/subscription?tab=addons');
};
</script>
