<template>
  <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.openSession') || 'Open Session' }}
      </h3>
      
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        {{ t('app.views.cashRegister.initialBalance') || 'Initial Balance' }}
      </label>
      <input 
        v-model="localBalance" 
        type="number" 
        step="0.01"
        class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
      
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="$emit('close')">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="primary" size="sm" @click="handleSave">
          {{ t('app.actions.save') || 'Save' }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import BaseButton from '@/components/ui/BaseButton.vue';

const { t } = useI18n();

const props = defineProps<{
  isOpen: boolean;
  initialBalance: number;
}>();

const emit = defineEmits<{
  close: [];
  save: [balance: number];
}>();

const localBalance = ref(props.initialBalance);

watch(() => props.initialBalance, (newVal) => {
  localBalance.value = newVal;
});

const handleSave = () => {
  emit('save', localBalance.value);
};
</script>
