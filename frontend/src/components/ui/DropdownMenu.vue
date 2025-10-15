<template>
  <div class="relative">
    <button
      @click.stop="toggleMenu"
      class="p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      :class="{ 'bg-gray-100 dark:bg-gray-800': internalIsOpen }"
      :aria-label="buttonLabel"
    >
      <EllipsisVerticalIcon class="h-5 w-5 text-gray-600 dark:text-gray-400" />
    </button>
    
    <!-- Dropdown Menu -->
    <div
      v-if="internalIsOpen"
      class="absolute right-0 mt-1 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5"
      :class="menuWidthClass"
      style="z-index: 9999;"
    >
      <div class="py-1" role="menu">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { EllipsisVerticalIcon } from '@heroicons/vue/24/outline';
import { useDropdownManager } from '@/composables/useDropdownManager';

interface Props {
  modelValue?: boolean;
  buttonLabel?: string;
  width?: 'sm' | 'md' | 'lg';
  id?: string;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  buttonLabel: 'Open menu',
  width: 'md',
  id: () => `dropdown-${Math.random().toString(36).substr(2, 9)}`
});

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'toggle': [value: boolean];
}>();

// Use the dropdown manager composable
const { isOpen: internalIsOpen, toggle: internalToggle, currentOpenDropdownId } = useDropdownManager(props.id);

const menuWidthClass = computed(() => {
  const widths = {
    sm: 'w-48',
    md: 'w-56',
    lg: 'w-64'
  };
  return widths[props.width];
});

const toggleMenu = () => {
  internalToggle();
  emit('update:modelValue', internalIsOpen.value);
  emit('toggle', internalIsOpen.value);
};

// Sync internal state with v-model
watch(() => props.modelValue, (newValue) => {
  if (newValue !== internalIsOpen.value) {
    if (newValue) {
      internalToggle();
    } else if (internalIsOpen.value) {
      internalToggle();
    }
  }
});

// Watch for changes in the global dropdown state
watch(currentOpenDropdownId, (newId) => {
  if (newId !== props.id && internalIsOpen.value) {
    internalIsOpen.value = false;
    emit('update:modelValue', false);
  }
});

// Emit changes to parent
watch(internalIsOpen, (newValue) => {
  emit('update:modelValue', newValue);
});

// Handle click outside to close menu
const handleClickOutside = () => {
  if (internalIsOpen.value) {
    internalIsOpen.value = false;
    emit('update:modelValue', false);
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
