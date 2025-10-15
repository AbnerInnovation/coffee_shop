import { ref } from 'vue';

// Global state to track which dropdown is currently open
const currentOpenDropdownId = ref<string | null>(null);

export function useDropdownManager(dropdownId: string) {
  const isOpen = ref(false);

  const open = () => {
    // Close any currently open dropdown
    if (currentOpenDropdownId.value && currentOpenDropdownId.value !== dropdownId) {
      // The previous dropdown will be closed via the watch on currentOpenDropdownId
    }
    currentOpenDropdownId.value = dropdownId;
    isOpen.value = true;
  };

  const close = () => {
    if (currentOpenDropdownId.value === dropdownId) {
      currentOpenDropdownId.value = null;
    }
    isOpen.value = false;
  };

  const toggle = () => {
    if (isOpen.value) {
      close();
    } else {
      open();
    }
  };

  // Watch for changes to the global state
  // If another dropdown opens, close this one
  const checkGlobalState = () => {
    if (currentOpenDropdownId.value !== dropdownId && isOpen.value) {
      isOpen.value = false;
    }
  };

  return {
    isOpen,
    open,
    close,
    toggle,
    checkGlobalState,
    currentOpenDropdownId
  };
}
