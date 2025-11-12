<template>
  <div class="mt-4">
    <div class="flex items-center justify-between mb-2">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ $t('app.views.orders.modals.new_order.persons.title') }}
      </label>
    </div>

    <!-- Person tabs -->
    <div class="space-y-2">
      <!-- Person tabs -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="(person, index) in persons"
          :key="index"
          type="button"
          @click="$emit('update:active-person-index', index)"
          class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors"
          :class="activePersonIndex === index
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          "
        >
          {{ person.name || $t('app.views.orders.modals.new_order.persons.person_label', { position: person.position }) }}
          <span class="ml-1 text-xs opacity-75">({{ person.items.length }})</span>
        </button>
        
        <button
          type="button"
          @click="$emit('add-person')"
          class="px-3 py-1.5 text-sm font-medium rounded-md bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-900/50"
        >
          + {{ $t('app.views.orders.modals.new_order.persons.add_person') }}
        </button>
      </div>

      <!-- Active person details -->
      <div class="bg-gray-50 dark:bg-gray-800 p-3 rounded-md">
        <button
          v-if="persons.length > 1"
          type="button"
          @click="$emit('remove-person', activePersonIndex)"
          class="mt-2 text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
        >
          {{ $t('app.views.orders.modals.new_order.persons.remove_person') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { OrderPerson } from '@/composables/useOrderForm';

interface Props {
  orderType: string;
  persons: OrderPerson[];
  activePersonIndex: number;
  disabled?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:active-person-index': [index: number];
  'add-person': [];
  'remove-person': [index: number];
  'update-person-name': [index: number, name: string];
}>();

const updatePersonName = (e: Event) => {
  const target = e.target as HTMLInputElement;
  emit('update-person-name', props.activePersonIndex, target.value);
};
</script>
