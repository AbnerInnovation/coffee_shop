<template>
  <div class="extras-selector">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white flex items-center">
        <PlusCircleIcon class="h-5 w-5 mr-2 text-indigo-600 dark:text-indigo-400" />
        {{ t('app.views.orders.extras.title') }}
      </h3>
    </div>

    <!-- Extras List -->
    <div v-if="extras.length > 0" class="space-y-2 mb-4">
      <div
        v-for="(extra, index) in extras"
        :key="index"
        class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
      >
        <div class="flex-1">
          <p class="text-sm font-medium text-gray-900 dark:text-white">
            {{ extra.name }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            ${{ extra.price.toFixed(2) }} × {{ extra.quantity }}
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-sm font-semibold text-gray-900 dark:text-white">
            ${{ (extra.price * extra.quantity).toFixed(2) }}
          </span>
          <button
            @click="removeExtra(index)"
            class="p-1 text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            :title="t('app.actions.delete')"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add Extra Form -->
    <div class="space-y-3">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {{ t('app.views.orders.extras.name') }}
        </label>
        <input
          v-model="newExtra.name"
          type="text"
          :placeholder="t('app.views.orders.extras.name_placeholder')"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
          @keyup.enter="addExtra"
        />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('app.views.orders.extras.price') }}
          </label>
          <input
            v-model.number="newExtra.price"
            type="number"
            step="0.01"
            min="0"
            :placeholder="t('app.views.orders.extras.price_placeholder')"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            @keyup.enter="addExtra"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {{ t('app.views.orders.extras.quantity') }}
          </label>
          <input
            v-model.number="newExtra.quantity"
            type="number"
            min="1"
            max="10"
            :placeholder="t('app.views.orders.extras.quantity_placeholder')"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:text-white"
            @keyup.enter="addExtra"
          />
        </div>
      </div>

      <button
        @click="addExtra"
        :disabled="!canAddExtra"
        class="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed dark:disabled:bg-gray-600 transition-colors"
      >
        <PlusIcon class="h-5 w-5 inline-block mr-1" />
        {{ t('app.views.orders.extras.add_button') }}
      </button>
    </div>

    <!-- Common Extras (Quick Add) -->
    <div v-if="commonExtras.length > 0" class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {{ t('app.views.orders.extras.common') }}
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="common in commonExtras"
          :key="common.name"
          @click="quickAddExtra(common)"
          class="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-indigo-100 dark:hover:bg-indigo-900 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
        >
          {{ common.name }} (${{ common.price.toFixed(2) }})
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { PlusCircleIcon, PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline';

export interface Extra {
  name: string;
  price: number;
  quantity: number;
}

const props = defineProps<{
  modelValue: Extra[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: Extra[]): void;
}>();

const { t } = useI18n();

const extras = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const newExtra = ref<Extra>({
  name: '',
  price: 0,
  quantity: 1
});

// Common extras that can be quickly added
const commonExtras = ref<Extra[]>([
  { name: 'Extra Tortillas', price: 15, quantity: 1 },
  { name: 'Extra Guacamole', price: 25, quantity: 1 },
  { name: 'Extra Queso', price: 20, quantity: 1 },
  { name: 'Extra Salsa', price: 10, quantity: 1 },
  { name: 'Extra Crema', price: 10, quantity: 1 },
]);

const canAddExtra = computed(() => {
  return newExtra.value.name.trim() !== '' && 
         newExtra.value.price >= 0 && 
         newExtra.value.quantity > 0 &&
         newExtra.value.quantity <= 10;
});

function addExtra() {
  if (!canAddExtra.value) return;

  extras.value = [...extras.value, { ...newExtra.value }];
  
  // Reset form
  newExtra.value = {
    name: '',
    price: 0,
    quantity: 1
  };
}

function quickAddExtra(common: Extra) {
  extras.value = [...extras.value, { ...common }];
}

function removeExtra(index: number) {
  extras.value = extras.value.filter((_, i) => i !== index);
}
</script>

<style scoped>
/* Remove number input spinners */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
