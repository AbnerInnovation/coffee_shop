<template>
  <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ modalTitle }}
      </h3>
      
      <!-- Name Field -->
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        {{ $t('app.forms.name') || 'Name' }}
      </label>
      <input 
        v-model="localName" 
        type="text" 
        class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        @keyup.enter="handleSave"
      />
      
      <!-- Description Field -->
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mt-4 mb-1">
        {{ $t('app.forms.description') || 'Description' }}
      </label>
      <textarea 
        v-model="localDescription" 
        rows="3" 
        class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      ></textarea>
      
      <!-- Visible in Kitchen Checkbox -->
      <div class="mt-4">
        <label class="flex items-center cursor-pointer">
          <input 
            type="checkbox" 
            v-model="localVisibleInKitchen"
            class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4"
          />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-200">
            {{ $t('app.forms.visible_in_kitchen') || 'Visible in Kitchen' }}
          </span>
        </label>
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          {{ $t('app.forms.visible_in_kitchen_help') || 'Uncheck to hide items from this category in the kitchen view (e.g., beverages)' }}
        </p>
      </div>
      
      <!-- Subscription Limit Alert -->
      <SubscriptionLimitAlert
        v-if="limitError"
        :message="limitError"
        :dismissible="false"
        class="mt-4"
      />
      
      <!-- Actions -->
      <div class="mt-6 flex justify-end space-x-3">
        <button 
          type="button" 
          class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-sm hover:bg-gray-50 dark:hover:bg-gray-800" 
          @click="$emit('cancel')"
        >
          {{ $t('app.actions.cancel') || 'Cancel' }}
        </button>
        <button 
          type="button" 
          class="px-4 py-2 rounded-md bg-indigo-600 text-white text-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500" 
          @click="handleSave"
        >
          {{ $t('app.actions.save') || 'Save' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import SubscriptionLimitAlert from '@/components/subscription/SubscriptionLimitAlert.vue';

const props = defineProps<{
  isOpen: boolean;
  name: string;
  description: string;
  visibleInKitchen: boolean;
  isEditing: boolean;
  limitError: string;
}>();

const emit = defineEmits<{
  save: [];
  cancel: [];
  'update:name': [value: string];
  'update:description': [value: string];
  'update:visibleInKitchen': [value: boolean];
}>();

const { t } = useI18n();

const localName = computed({
  get: () => props.name,
  set: (value) => emit('update:name', value)
});

const localDescription = computed({
  get: () => props.description,
  set: (value) => emit('update:description', value)
});

const localVisibleInKitchen = computed({
  get: () => props.visibleInKitchen,
  set: (value) => emit('update:visibleInKitchen', value)
});

const modalTitle = computed(() => {
  const action = props.isEditing ? (t('app.actions.edit') || 'Edit') : (t('app.actions.add') || 'Add');
  const entity = t('app.forms.category') || 'Category';
  return `${action} ${entity}`;
});

function handleSave() {
  emit('save');
}
</script>
