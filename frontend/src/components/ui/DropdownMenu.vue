<template>
  <div class="relative">
    <button
      type="button"
      ref="buttonRef"
      @click.stop="toggleMenu"
      class="p-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors relative z-10"
      :class="{ 'bg-gray-100 dark:bg-gray-800': internalIsOpen }"
      :aria-label="buttonLabel"
    >
      <EllipsisVerticalIcon class="h-5 w-5 text-gray-600 dark:text-gray-400" />
    </button>
    
    <!-- Dropdown Menu -->
    <div
      v-if="internalIsOpen"
      ref="menuRef"
      class="fixed rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 max-h-[80vh] overflow-y-auto"
      :class="menuWidthClass"
      :style="menuStyle"
    >
      <div class="py-1" role="menu">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { EllipsisVerticalIcon } from '@heroicons/vue/24/outline';
import { useDropdownManager } from '@/composables/useDropdownManager';

interface Props {
  modelValue?: boolean;
  buttonLabel?: string;
  width?: 'sm' | 'md' | 'lg';
  id?: string;
  elevateParent?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  buttonLabel: 'Open menu',
  width: 'md',
  id: () => `dropdown-${Math.random().toString(36).substr(2, 9)}`,
  elevateParent: true
});

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  'toggle': [value: boolean];
}>();

// Use the dropdown manager composable
const { isOpen: internalIsOpen, toggle: internalToggle, currentOpenDropdownId } = useDropdownManager(props.id);

const buttonRef = ref<HTMLElement | null>(null);
const menuRef = ref<HTMLElement | null>(null);
const menuPosition = ref<{ top: number | 'auto', right: number, bottom: number | 'auto' }>({ 
  top: 0, 
  right: 0, 
  bottom: 'auto' 
});

const menuWidthClass = computed(() => {
  const widths = {
    sm: 'w-48',
    md: 'w-56',
    lg: 'w-64'
  };
  return widths[props.width];
});

const menuStyle = computed(() => ({
  top: menuPosition.value.top !== 'auto' ? `${menuPosition.value.top}px` : 'auto',
  bottom: menuPosition.value.bottom !== 'auto' ? `${menuPosition.value.bottom}px` : 'auto',
  right: `${menuPosition.value.right}px`,
  zIndex: 9999
}));

const updateMenuPosition = () => {
  if (buttonRef.value && menuRef.value) {
    const rect = buttonRef.value.getBoundingClientRect();
    const menuHeight = menuRef.value.offsetHeight || 200; // Estimate if not rendered yet
    const spaceBelow = window.innerHeight - rect.bottom - 10; // 10px bottom padding
    const spaceAbove = rect.top - 10; // 10px top padding
    
    // Determine if menu should open upward or downward
    // Prefer downward unless there's clearly more space above
    const openUpward = spaceBelow < menuHeight && spaceAbove > spaceBelow && spaceAbove > menuHeight;
    
    if (openUpward) {
      // Open upward - position from bottom
      const bottomPos = window.innerHeight - rect.top + 4;
      menuPosition.value = {
        top: 'auto',
        bottom: bottomPos,
        right: window.innerWidth - rect.right
      };
    } else {
      // Open downward (default) - position from top
      const topPos = rect.bottom + 4;
      // Ensure menu doesn't go below viewport
      const maxTop = Math.min(topPos, window.innerHeight - menuHeight - 10);
      menuPosition.value = {
        top: maxTop,
        bottom: 'auto',
        right: window.innerWidth - rect.right
      };
    }
  }
};

const toggleMenu = () => {
  internalToggle();
  emit('update:modelValue', internalIsOpen.value);
  emit('toggle', internalIsOpen.value);
  
  if (internalIsOpen.value) {
    nextTick(() => {
      updateMenuPosition();
    });
  }
};

// Sync internal state with v-model
watch(() => props.modelValue, (newValue) => {
  if (newValue !== internalIsOpen.value) {
    if (newValue) {
      internalToggle();
      nextTick(() => {
        updateMenuPosition();
      });
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
  
  // Automatically elevate parent container if enabled
  if (props.elevateParent) {
    const container = document.querySelector(`[data-dropdown-container="${props.id}"]`);
    if (container) {
      if (newValue) {
        container.classList.add('z-50');
      } else {
        container.classList.remove('z-50');
      }
    }
  }
});

// Handle click outside to close menu
const handleClickOutside = (event: MouseEvent) => {
  if (internalIsOpen.value) {
    const target = event.target as Node;
    const isClickInsideButton = buttonRef.value?.contains(target);
    const isClickInsideMenu = menuRef.value?.contains(target);
    
    if (!isClickInsideButton && !isClickInsideMenu) {
      internalIsOpen.value = false;
      emit('update:modelValue', false);
    }
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('scroll', updateMenuPosition, true);
  window.addEventListener('resize', updateMenuPosition);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('scroll', updateMenuPosition, true);
  window.removeEventListener('resize', updateMenuPosition);
  
  // Clean up parent elevation on unmount
  if (props.elevateParent) {
    const container = document.querySelector(`[data-dropdown-container="${props.id}"]`);
    if (container) {
      container.classList.remove('z-50');
    }
  }
});
</script>
