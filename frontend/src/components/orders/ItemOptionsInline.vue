<template>
  <div class="mt-6">
    <!-- Back button -->
    <button @click="$emit('back')"
      class="mb-4 flex items-center text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300">
      <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
      </svg>
      Volver al menú
    </button>

    <!-- Item Options Content -->
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">{{ item.name }}</h3>
      <p v-if="item.description" class="text-sm text-gray-500 dark:text-gray-400">{{ item.description }}</p>

      <!-- Variants -->
      <div v-if="item.variants?.length" class="space-y-2">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Opciones</label>
        
        <!-- Base item option - only show if base price > 0 -->
        <div v-if="item.price && item.price > 0" @click="selectedVariant = null"
          class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors"
          :class="!selectedVariant ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-300 dark:border-gray-700'">
          <div class="flex-1">
            <p class="font-medium text-gray-900 dark:text-gray-100">Artículo base</p>
            <div class="flex items-center gap-2">
              <!-- Show original price if there's a discount -->
              <p v-if="item.discount_price && item.discount_price > 0" class="text-sm text-gray-500 dark:text-gray-400 line-through">
                ${{ (item.price || 0).toFixed(2) }}
              </p>
              <!-- Show effective price -->
              <p class="text-sm" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400 font-semibold' : 'text-gray-600 dark:text-gray-400'">
                ${{ (item.discount_price && item.discount_price > 0 ? item.discount_price : item.price || 0).toFixed(2) }}
              </p>
              <!-- Show discount badge -->
              <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                Oferta
              </span>
            </div>
          </div>
          <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
            :class="!selectedVariant ? 'border-indigo-600 bg-indigo-600' : 'border-gray-300 dark:border-gray-600'">
            <div v-if="!selectedVariant" class="w-2 h-2 rounded-full bg-white"></div>
          </div>
        </div>

        <!-- Variant options -->
        <div v-for="variant in item.variants" :key="variant.id" @click="selectedVariant = variant"
          class="flex items-center p-3 border rounded-lg cursor-pointer transition-colors"
          :class="selectedVariant?.id === variant.id ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' : 'border-gray-300 dark:border-gray-700'">
          <div class="flex-1">
            <p class="font-medium text-gray-900 dark:text-gray-100">{{ variant.name }}</p>
            <div class="flex items-center gap-2">
              <!-- Show original price if there's a discount -->
              <p v-if="variant.discount_price && variant.discount_price > 0" class="text-sm text-gray-500 dark:text-gray-400 line-through">
                ${{ (variant.price || 0).toFixed(2) }}
              </p>
              <!-- Show effective price -->
              <p class="text-sm" :class="variant.discount_price && variant.discount_price > 0 ? 'text-green-600 dark:text-green-400 font-semibold' : 'text-gray-600 dark:text-gray-400'">
                ${{ getVariantPrice(variant).toFixed(2) }}
              </p>
              <!-- Show discount badge -->
              <span v-if="variant.discount_price && variant.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                Oferta
              </span>
            </div>
          </div>
          <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
            :class="selectedVariant?.id === variant.id ? 'border-indigo-600 bg-indigo-600' : 'border-gray-300 dark:border-gray-600'">
            <div v-if="selectedVariant?.id === variant.id" class="w-2 h-2 rounded-full bg-white"></div>
          </div>
        </div>
      </div>

      <!-- Notes -->
      <div>
        <SpecialNotesBuilder v-if="item.ingredients" :ingredients="item.ingredients" v-model="specialNote"
          :top-notes="topNotes" />
        <div v-else>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Instrucciones especiales
          </label>
          <textarea v-model="notes" rows="3"
            class="w-full rounded-lg border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="¿Alguna petición especial?" />
        </div>
      </div>

      <!-- Add button -->
      <button @click="handleAdd"
        class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors">
        Agregar a la orden
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import SpecialNotesBuilder from './SpecialNotesBuilder.vue';
import type { ExtendedMenuItem, MenuItemVariant } from '@/types/order';

interface Props {
  item: ExtendedMenuItem;
  topNotes: string[];
  getVariantPrice: (variant: MenuItemVariant) => number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'back'): void;
  (e: 'add', data: { item: ExtendedMenuItem; variant: MenuItemVariant | null; quantity: number; notes: string }): void;
}>();

// Internal state - same as ItemOptionsModal
const selectedVariant = ref<MenuItemVariant | null>(null);
const specialNote = ref('');
const notes = ref('');
const quantity = ref(1);

// Reset when item changes - same as ItemOptionsModal
watch(() => props.item, (newItem) => {
  if (newItem) {
    selectedVariant.value = null;
    specialNote.value = '';
    notes.value = '';
    quantity.value = 1;
  }
});

function handleAdd() {
  const finalNotes = specialNote.value || notes.value;
  
  emit('add', {
    item: props.item,
    variant: selectedVariant.value,
    quantity: quantity.value,
    notes: finalNotes
  });
  
  // Reset after adding - same as ItemOptionsModal
  selectedVariant.value = null;
  specialNote.value = '';
  notes.value = '';
  quantity.value = 1;
}
</script>
