import { ref, computed } from 'vue';
import type { OrderPerson, PersonOrderItem } from './useMultipleDiners';

export interface OrderFormData {
  type: 'Dine-in' | 'Takeaway' | 'Delivery';
  tableId: number | null;
  customerName: string;
  notes: string;
}

export interface OrderItemWithDetails {
  id?: number;
  menu_item_id: number;
  variant_id?: number | null;
  name: string;
  variant_name?: string;
  category?: string;
  quantity: number;
  unit_price: number;
  price?: number;
  notes?: string;
  status?: string;
  extras?: Array<{ name: string; price: number; quantity: number }>;
}

// Re-export for convenience
export type { OrderPerson, PersonOrderItem };

export function useOrderForm() {
  // Form state
  const form = ref<OrderFormData>({
    type: 'Dine-in',
    tableId: null,
    customerName: '',
    notes: ''
  });

  // Multi-diner state
  const useMultipleDiners = ref(false);
  const activePersonIndex = ref(0);
  const persons = ref<OrderPerson[]>([
    { position: 1, name: '', items: [] }
  ]);

  // Selected items (for simple orders)
  const selectedItems = ref<OrderItemWithDetails[]>([]);

  // Payment state
  const markAsPaid = ref(false);
  const selectedPaymentMethod = ref<'cash' | 'card' | 'digital' | 'other'>('cash');

  // Computed
  const activePerson = computed(() => persons.value[activePersonIndex.value]);

  const allItems = computed(() => {
    if (useMultipleDiners.value) {
      return persons.value.flatMap(p => p.items);
    }
    return selectedItems.value;
  });

  const totalAmount = computed(() => {
    if (useMultipleDiners.value) {
      return persons.value.reduce((sum, person) => 
        sum + person.items.reduce((itemSum, item) => 
          itemSum + ((item.unit_price || 0) * item.quantity), 0
        ), 0
      );
    }
    return selectedItems.value.reduce((sum, item) => 
      sum + ((item.unit_price || 0) * item.quantity), 0
    );
  });

  // Methods
  const addPerson = () => {
    persons.value.push({
      position: persons.value.length + 1,
      name: '',
      items: []
    });
    activePersonIndex.value = persons.value.length - 1;
  };

  const removePerson = (index: number) => {
    if (persons.value.length > 1) {
      persons.value.splice(index, 1);
      // Update positions
      persons.value.forEach((person, idx) => {
        person.position = idx + 1;
      });
      // Adjust active index
      if (activePersonIndex.value >= persons.value.length) {
        activePersonIndex.value = persons.value.length - 1;
      }
    }
  };

  const addItemToPerson = (personIndex: number, item: OrderItemWithDetails) => {
    persons.value[personIndex].items.push(item);
  };

  const removeItemFromPerson = (personIndex: number, itemIndex: number) => {
    persons.value[personIndex].items.splice(itemIndex, 1);
  };

  const addItemToOrder = (item: OrderItemWithDetails) => {
    if (useMultipleDiners.value) {
      addItemToPerson(activePersonIndex.value, item);
    } else {
      const existingIndex = selectedItems.value.findIndex(
        i => i.menu_item_id === item.menu_item_id && i.variant_id === item.variant_id
      );
      
      if (existingIndex >= 0) {
        selectedItems.value[existingIndex].quantity += item.quantity;
      } else {
        selectedItems.value.push(item);
      }
    }
  };

  const increaseQuantity = (item: OrderItemWithDetails) => {
    item.quantity++;
  };

  const decreaseQuantity = (item: OrderItemWithDetails) => {
    if (item.quantity > 1) {
      item.quantity--;
    } else {
      const index = selectedItems.value.findIndex(i => i === item);
      if (index >= 0) {
        selectedItems.value.splice(index, 1);
      }
    }
  };

  const resetForm = () => {
    form.value = {
      type: 'Dine-in',
      tableId: null,
      customerName: '',
      notes: ''
    };
    useMultipleDiners.value = false;
    activePersonIndex.value = 0;
    persons.value = [{ position: 1, name: '', items: [] }];
    selectedItems.value = [];
    markAsPaid.value = false;
    selectedPaymentMethod.value = 'cash';
  };

  return {
    // State
    form,
    useMultipleDiners,
    activePersonIndex,
    persons,
    selectedItems,
    markAsPaid,
    selectedPaymentMethod,
    
    // Computed
    activePerson,
    allItems,
    totalAmount,
    
    // Methods
    addPerson,
    removePerson,
    addItemToPerson,
    removeItemFromPerson,
    addItemToOrder,
    increaseQuantity,
    decreaseQuantity,
    resetForm
  };
}
