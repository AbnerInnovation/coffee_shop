<template>
  <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-2xl rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.closeSession') || 'Close Session' }}
      </h3>
      
      <!-- Toggle for denomination counting -->
      <div class="mb-4">
        <label class="flex items-center cursor-pointer">
          <input 
            type="checkbox" 
            v-model="localUseDenominations" 
            class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-200">
            {{ t('app.views.cashRegister.useDenominationCounting') || 'Count denominations' }}
          </span>
        </label>
      </div>

      <!-- Denomination Counter -->
      <div v-if="localUseDenominations" class="mb-4">
        <DenominationCounter v-model="localDenominations" @update:total="localBalance = $event" />
      </div>

      <!-- Manual balance input -->
      <div v-else class="mb-4">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
          {{ t('app.views.cashRegister.actualBalance') || 'Actual Balance' }}
        </label>
        <input 
          v-model="localBalance" 
          type="number" 
          step="0.01"
          class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
        {{ t('app.views.cashRegister.notes') || 'Notes' }}
      </label>
      <textarea 
        v-model="localNotes" 
        rows="3"
        class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      ></textarea>
      
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="$emit('close')">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="danger" size="sm" @click="handleSave">
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
import DenominationCounter from '@/components/DenominationCounter.vue';
import type { Denominations } from '@/utils/cashRegisterHelpers';

const { t } = useI18n();

const props = defineProps<{
  isOpen: boolean;
  actualBalance: number;
  notes: string;
  useDenominations: boolean;
  denominations: Denominations;
}>();

const emit = defineEmits<{
  close: [];
  save: [data: { balance: number; notes: string; useDenominations: boolean; denominations: Denominations }];
}>();

const localBalance = ref(props.actualBalance);
const localNotes = ref(props.notes);
const localUseDenominations = ref(props.useDenominations);
const localDenominations = ref(props.denominations);

watch(() => props.actualBalance, (newVal) => localBalance.value = newVal);
watch(() => props.notes, (newVal) => localNotes.value = newVal);
watch(() => props.useDenominations, (newVal) => localUseDenominations.value = newVal);
watch(() => props.denominations, (newVal) => localDenominations.value = newVal, { deep: true });

const handleSave = () => {
  emit('save', {
    balance: localBalance.value,
    notes: localNotes.value,
    useDenominations: localUseDenominations.value,
    denominations: localDenominations.value
  });
};
</script>
