<template>
  <!-- Loading State -->
  <div v-if="loading" class="text-center py-8">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
    <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">
      {{ t('app.views.tables.loading') }}
    </p>
  </div>

  <!-- Error State -->
  <div 
    v-else-if="error" 
    class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 p-4 mb-4 rounded-r-lg"
  >
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
  <div 
    v-else-if="isEmpty" 
    class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow"
  >
    <svg 
      class="mx-auto h-12 w-12 text-gray-400" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor" 
      aria-hidden="true"
    >
      <path 
        stroke-linecap="round" 
        stroke-linejoin="round" 
        stroke-width="2" 
        d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" 
      />
    </svg>
    <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
      {{ t('app.views.tables.no_tables') }}
    </h3>
    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      {{ t('app.views.tables.no_tables_description') }}
    </p>
    <div v-if="canManageTables" class="mt-6">
      <BaseButton variant="primary" @click="$emit('add-table')">
        <template #icon>
          <PlusIcon class="h-5 w-5" aria-hidden="true" />
        </template>
        {{ t('app.views.tables.add_table') }}
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { XCircleIcon, PlusIcon } from '@heroicons/vue/24/outline';
import BaseButton from '@/components/ui/BaseButton.vue';

interface Props {
  loading?: boolean;
  error?: string;
  isEmpty?: boolean;
  canManageTables?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  error: '',
  isEmpty: false,
  canManageTables: false
});

defineEmits<{
  'add-table': [];
}>();

const { t } = useI18n();
</script>
