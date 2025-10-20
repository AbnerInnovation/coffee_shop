<template>
  <div class="rounded-lg border-2 border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 p-4">
    <div class="flex items-start gap-3">
      <!-- Icon -->
      <div class="flex-shrink-0">
        <ExclamationTriangleIcon class="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
      </div>
      
      <!-- Content -->
      <div class="flex-1 min-w-0">
        <h3 class="text-sm font-semibold text-yellow-800 dark:text-yellow-300 mb-1">
          {{ t('app.subscription.limit_reached') }}
        </h3>
        <p class="text-sm text-yellow-700 dark:text-yellow-400 mb-3">
          {{ message }}
        </p>
        
        <!-- Action Button (only for admin) -->
        <button
          v-if="canUpgrade"
          @click="goToPlans"
          class="inline-flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2"
        >
          <ArrowUpCircleIcon class="h-5 w-5" />
          {{ t('app.subscription.upgrade_plan') }}
        </button>
      </div>
      
      <!-- Close button -->
      <button
        v-if="dismissible"
        @click="$emit('close')"
        class="flex-shrink-0 text-yellow-600 dark:text-yellow-400 hover:text-yellow-800 dark:hover:text-yellow-200 transition-colors"
      >
        <XMarkIcon class="h-5 w-5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { ExclamationTriangleIcon, ArrowUpCircleIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';

const { t } = useI18n();
const router = useRouter();
const authStore = useAuthStore();

interface Props {
  message: string;
  dismissible?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  dismissible: true
});

defineEmits<{
  close: [];
}>();

const canUpgrade = computed(() => {
  const role = authStore.user?.role;
  return role === 'admin' || role === 'sysadmin';
});

function goToPlans() {
  router.push({ path: '/subscription', query: { openModal: 'true' } });
}
</script>
