<template>
  <div class="space-y-4">
    <h4 class="font-medium text-gray-900 dark:text-gray-100 mb-3">
      {{ t('app.views.cashRegister.countDenominations') || 'Count Denominations (MXN)' }}
    </h4>
    
    <!-- Bills -->
    <div class="space-y-3">
      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.cashRegister.bills') || 'Bills' }}</h5>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$1000</label>
          <input v-model.number="denominations.bills_1000" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.bills_1000 * 1000).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$500</label>
          <input v-model.number="denominations.bills_500" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.bills_500 * 500).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$200</label>
          <input v-model.number="denominations.bills_200" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.bills_200 * 200).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$100</label>
          <input v-model.number="denominations.bills_100" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.bills_100 * 100).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$50</label>
          <input v-model.number="denominations.bills_50" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.bills_50 * 50).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$20</label>
          <input v-model.number="denominations.bills_20" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.bills_20 * 20).toFixed(2) }}</p>
        </div>
      </div>
    </div>
    
    <!-- Coins -->
    <div class="space-y-3">
      <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.cashRegister.coins') || 'Coins' }}</h5>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$20</label>
          <input v-model.number="denominations.coins_20" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.coins_20 * 20).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$10</label>
          <input v-model.number="denominations.coins_10" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.coins_10 * 10).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$5</label>
          <input v-model.number="denominations.coins_5" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.coins_5 * 5).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$2</label>
          <input v-model.number="denominations.coins_2" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.coins_2 * 2).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$1</label>
          <input v-model.number="denominations.coins_1" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.coins_1 * 1).toFixed(2) }}</p>
        </div>
        
        <div>
          <label class="block text-xs text-gray-600 dark:text-gray-400 mb-1">$0.50</label>
          <input v-model.number="denominations.coins_50_cent" type="number" min="0" step="1"
            @input="calculateTotal"
            class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          <p class="text-xs text-gray-500 mt-1">${{ (denominations.coins_50_cent * 0.50).toFixed(2) }}</p>
        </div>
      </div>
    </div>
    
    <!-- Total -->
    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
      <div class="flex justify-between items-center">
        <span class="text-lg font-medium text-gray-900 dark:text-gray-100">
          {{ t('app.views.cashRegister.totalCounted') || 'Total Counted' }}
        </span>
        <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
          ${{ total.toFixed(2) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  modelValue?: {
    bills_1000: number;
    bills_500: number;
    bills_200: number;
    bills_100: number;
    bills_50: number;
    bills_20: number;
    coins_20: number;
    coins_10: number;
    coins_5: number;
    coins_2: number;
    coins_1: number;
    coins_50_cent: number;
  }
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
  (e: 'update:total', value: number): void
}>()

const denominations = ref({
  bills_1000: props.modelValue?.bills_1000 || 0,
  bills_500: props.modelValue?.bills_500 || 0,
  bills_200: props.modelValue?.bills_200 || 0,
  bills_100: props.modelValue?.bills_100 || 0,
  bills_50: props.modelValue?.bills_50 || 0,
  bills_20: props.modelValue?.bills_20 || 0,
  coins_20: props.modelValue?.coins_20 || 0,
  coins_10: props.modelValue?.coins_10 || 0,
  coins_5: props.modelValue?.coins_5 || 0,
  coins_2: props.modelValue?.coins_2 || 0,
  coins_1: props.modelValue?.coins_1 || 0,
  coins_50_cent: props.modelValue?.coins_50_cent || 0
})

const total = ref(0)

const calculateTotal = () => {
  total.value = 
    denominations.value.bills_1000 * 1000.00 +
    denominations.value.bills_500 * 500.00 +
    denominations.value.bills_200 * 200.00 +
    denominations.value.bills_100 * 100.00 +
    denominations.value.bills_50 * 50.00 +
    denominations.value.bills_20 * 20.00 +
    denominations.value.coins_20 * 20.00 +
    denominations.value.coins_10 * 10.00 +
    denominations.value.coins_5 * 5.00 +
    denominations.value.coins_2 * 2.00 +
    denominations.value.coins_1 * 1.00 +
    denominations.value.coins_50_cent * 0.50
  
  emit('update:modelValue', denominations.value)
  emit('update:total', total.value)
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    denominations.value = { ...newValue }
    calculateTotal()
  }
}, { deep: true })

// Initialize total
calculateTotal()
</script>
