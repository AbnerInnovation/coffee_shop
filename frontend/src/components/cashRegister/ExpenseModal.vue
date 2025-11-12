<template>
  <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.addExpense') || 'Add Expense' }}
      </h3>
      
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.expenseAmount') || 'Amount' }}
          </label>
          <input 
            v-model="localAmount" 
            type="number" 
            step="0.01" 
            min="0"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.expenseDescription') || 'Description' }}
          </label>
          <input 
            v-model="localDescription" 
            type="text"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
            {{ t('app.views.cashRegister.expenseCategory') || 'Category (Optional)' }}
          </label>
          <select 
            v-model="localCategory"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="">{{ t('app.views.cashRegister.selectCategory') || 'Select a category' }}</option>
            <option value="supplies">{{ t('app.views.cashRegister.categorySupplies') || 'Supplies' }}</option>
            <option value="utilities">{{ t('app.views.cashRegister.categoryUtilities') || 'Utilities' }}</option>
            <option value="maintenance">{{ t('app.views.cashRegister.categoryMaintenance') || 'Maintenance' }}</option>
            <option value="inventory">{{ t('app.views.cashRegister.categoryInventory') || 'Inventory' }}</option>
            <option value="other">{{ t('app.views.cashRegister.categoryOther') || 'Other' }}</option>
          </select>
        </div>
      </div>
      
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="$emit('close')">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="warning" size="sm" @click="handleSave">
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
  amount: number;
  description: string;
  category: string;
}>();

const emit = defineEmits<{
  close: [];
  save: [data: { amount: number; description: string; category: string }];
}>();

const localAmount = ref(props.amount);
const localDescription = ref(props.description);
const localCategory = ref(props.category);

watch(() => props.amount, (newVal) => localAmount.value = newVal);
watch(() => props.description, (newVal) => localDescription.value = newVal);
watch(() => props.category, (newVal) => localCategory.value = newVal);

const handleSave = () => {
  emit('save', {
    amount: localAmount.value,
    description: localDescription.value,
    category: localCategory.value
  });
};
</script>
