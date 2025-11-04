<template>
  <div v-if="isOpen" class="fixed inset-0 z-[10003] overflow-y-auto">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-75 transition-opacity pointer-events-none"></div>
    
    <!-- Modal -->
    <div class="flex min-h-full items-center justify-center p-4 pointer-events-none">
      <div class="relative w-full max-w-md transform overflow-hidden rounded-lg bg-white dark:bg-gray-800 shadow-xl transition-all pointer-events-auto">
        <!-- Header -->
        <div class="bg-red-50 dark:bg-red-900/20 px-6 py-4 border-b border-red-200 dark:border-red-800">
          <div class="flex items-center">
            <ExclamationTriangleIcon class="h-8 w-8 text-red-600 dark:text-red-400 mr-3" />
            <h3 class="text-lg font-semibold text-red-900 dark:text-red-100">
              {{ t('app.subscription.account_suspended.title') }}
            </h3>
          </div>
        </div>

        <!-- Content -->
        <div class="px-6 py-4">
          <p class="text-sm text-gray-700 dark:text-gray-300 mb-4">
            {{ message }}
          </p>

          <div v-if="daysRemaining !== undefined && daysRemaining > 0" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3 mb-4">
            <p class="text-sm text-yellow-800 dark:text-yellow-200">
              <strong>{{ t('app.subscription.account_suspended.days_remaining') }}:</strong> {{ daysRemaining }} {{ t('app.subscription.account_suspended.days') }}
            </p>
          </div>

          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <p class="text-sm text-blue-800 dark:text-blue-200">
              <strong>{{ t('app.subscription.account_suspended.what_to_do') }}:</strong>
            </p>
            <ul class="list-disc list-inside text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1">
              <li>{{ t('app.subscription.account_suspended.contact_admin') }}</li>
              <li>{{ t('app.subscription.account_suspended.renew_plan') }}</li>
              <li>{{ t('app.subscription.account_suspended.update_payment') }}</li>
            </ul>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 dark:bg-gray-900 px-6 py-4 flex justify-end space-x-3">
          <button
            v-if="canViewSubscription"
            @click="goToSubscription"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
          >
            {{ t('app.subscription.account_suspended.view_subscription') }}
          </button>
          <button
            @click="logout"
            class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            {{ t('app.subscription.account_suspended.logout') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';

interface Props {
  isOpen: boolean;
  message: string;
  status?: string;
  daysRemaining?: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const router = useRouter();
const { t } = useI18n();
const authStore = useAuthStore();

const canViewSubscription = computed(() => {
  return authStore.user?.role === 'admin' || authStore.user?.role === 'sysadmin';
});

const goToSubscription = () => {
  emit('close');
  router.push('/subscription');
};

const logout = () => {
  emit('close');
  authStore.logout();
  router.push('/login');
};
</script>
