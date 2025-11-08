import { ref } from 'vue';
import type { ExtendedMenuItem, MenuItemVariant } from '@/types/order';
import type { Extra } from '@/components/orders/ExtrasSelector.vue';

export function useItemSelection() {
  // Selected item state
  const selectedItem = ref<ExtendedMenuItem | null>(null);
  const selectedVariant = ref<MenuItemVariant | null>(null);
  const itemNotes = ref('');
  const itemSpecialNote = ref('');
  const itemExtras = ref<Extra[]>([]);
  const showItemModal = ref(false);
  const showItemOptionsModal = ref(false);
  const showingItemOptions = ref(false);

  // Reset item selection
  function resetItemSelection() {
    selectedItem.value = null;
    selectedVariant.value = null;
    itemNotes.value = '';
    itemSpecialNote.value = '';
    itemExtras.value = [];
    showItemModal.value = false;
    showItemOptionsModal.value = false;
    showingItemOptions.value = false;
  }

  // Select item
  function selectItem(menuItem: ExtendedMenuItem, isMobile: boolean) {
    selectedItem.value = { ...menuItem };
    
    if (isMobile) {
      // In mobile, show options inline (stepper approach)
      showingItemOptions.value = true;
    } else {
      // In desktop, show modal
      showItemOptionsModal.value = true;
    }
  }

  return {
    // State
    selectedItem,
    selectedVariant,
    itemNotes,
    itemSpecialNote,
    itemExtras,
    showItemModal,
    showItemOptionsModal,
    showingItemOptions,
    
    // Methods
    resetItemSelection,
    selectItem
  };
}
