import { ref, computed } from 'vue';
import type { Extra } from '@/components/orders/ExtrasSelector.vue';

/**
 * Interfaz para un item en la orden de una persona
 */
export interface PersonOrderItem {
  menu_item_id: number;
  variant_id?: number | null;
  quantity: number;
  notes?: string;
  special_instructions?: string;
  unit_price?: number;
  extras?: Extra[];
}

/**
 * Interfaz para una persona/comensal en la orden
 */
export interface OrderPerson {
  id?: number;
  name: string;
  position: number;
  items: PersonOrderItem[];
}

/**
 * Composable para gestionar órdenes con múltiples comensales
 * Separa la lógica de gestión de personas/comensales del componente principal
 */
export function useMultipleDiners() {
  // Estado
  const useMultipleDiners = ref(false);
  const activePersonIndex = ref(0);
  const persons = ref<OrderPerson[]>([
    { name: '', position: 1, items: [] }
  ]);

  // Computed
  const activePerson = computed(() => persons.value[activePersonIndex.value]);
  
  const totalPersons = computed(() => persons.value.length);
  
  const hasMultiplePersons = computed(() => persons.value.length > 1);

  /**
   * Agrega una nueva persona a la orden
   */
  function addPerson() {
    persons.value.push({
      name: '',
      position: persons.value.length + 1,
      items: []
    });
    activePersonIndex.value = persons.value.length - 1;
  }

  /**
   * Elimina una persona de la orden
   * No permite eliminar si solo hay una persona
   */
  function removePerson(index: number) {
    if (persons.value.length === 1) {
      return false;
    }

    persons.value.splice(index, 1);
    
    // Reajustar positions
    persons.value.forEach((person, idx) => {
      person.position = idx + 1;
    });
    
    // Ajustar activePersonIndex si es necesario
    if (activePersonIndex.value >= persons.value.length) {
      activePersonIndex.value = persons.value.length - 1;
    }

    return true;
  }

  /**
   * Actualiza el nombre de una persona
   */
  function updatePersonName(index: number, name: string) {
    if (persons.value[index]) {
      persons.value[index].name = name;
    }
  }

  /**
   * Agrega un item a la persona activa
   */
  function addItemToActivePerson(item: PersonOrderItem) {
    if (activePerson.value) {
      activePerson.value.items.push(item);
    }
  }

  /**
   * Agrega un item a una persona específica
   */
  function addItemToPerson(personIndex: number, item: PersonOrderItem) {
    if (persons.value[personIndex]) {
      persons.value[personIndex].items.push(item);
    }
  }

  /**
   * Elimina un item de una persona
   */
  function removeItemFromPerson(personIndex: number, itemIndex: number) {
    if (persons.value[personIndex]?.items[itemIndex]) {
      persons.value[personIndex].items.splice(itemIndex, 1);
    }
  }

  /**
   * Aumenta la cantidad de un item
   */
  function increaseItemQuantity(personIndex: number, itemIndex: number) {
    const item = persons.value[personIndex]?.items[itemIndex];
    if (item) {
      item.quantity++;
    }
  }

  /**
   * Disminuye la cantidad de un item
   * Si llega a 0, elimina el item
   */
  function decreaseItemQuantity(personIndex: number, itemIndex: number) {
    const item = persons.value[personIndex]?.items[itemIndex];
    if (item) {
      if (item.quantity > 1) {
        item.quantity--;
      } else {
        removeItemFromPerson(personIndex, itemIndex);
      }
    }
  }

  /**
   * Obtiene todos los items de todas las personas
   */
  function getAllItems(): PersonOrderItem[] {
    return persons.value.flatMap(person => person.items);
  }

  /**
   * Calcula el total de items (suma de cantidades)
   */
  function getTotalItemsCount(): number {
    return persons.value.reduce((total, person) => 
      total + person.items.reduce((sum, item) => sum + item.quantity, 0), 
      0
    );
  }

  /**
   * Calcula el total de la orden (suma de precios * cantidades)
   */
  function getTotalAmount(): number {
    return persons.value.reduce((total, person) => 
      total + person.items.reduce((sum, item) => 
        sum + ((item.unit_price || 0) * item.quantity), 
        0
      ), 
      0
    );
  }

  /**
   * Calcula el total de una persona específica
   */
  function getPersonTotal(personIndex: number): number {
    const person = persons.value[personIndex];
    if (!person) return 0;
    
    return person.items.reduce((sum, item) => 
      sum + ((item.unit_price || 0) * item.quantity), 
      0
    );
  }

  /**
   * Resetea el estado a valores iniciales
   */
  function reset() {
    useMultipleDiners.value = false;
    activePersonIndex.value = 0;
    persons.value = [{ name: '', position: 1, items: [] }];
  }

  /**
   * Activa/desactiva el modo de múltiples comensales
   */
  function toggleMultipleDiners() {
    useMultipleDiners.value = !useMultipleDiners.value;
    
    // Si se desactiva, resetear a una sola persona
    if (!useMultipleDiners.value) {
      // Combinar todos los items en la primera persona
      const allItems = getAllItems();
      persons.value = [{
        name: '',
        position: 1,
        items: allItems
      }];
      activePersonIndex.value = 0;
    }
  }

  /**
   * Carga datos de personas desde una orden existente
   */
  function loadPersonsFromOrder(orderPersons: OrderPerson[]) {
    if (orderPersons && orderPersons.length > 0) {
      persons.value = orderPersons.map((person, index) => ({
        id: person.id,
        name: person.name || '',
        position: index + 1,
        items: person.items || []
      }));
      useMultipleDiners.value = true;
      activePersonIndex.value = 0;
    }
  }

  return {
    // Estado
    useMultipleDiners,
    activePersonIndex,
    persons,
    
    // Computed
    activePerson,
    totalPersons,
    hasMultiplePersons,
    
    // Métodos de gestión de personas
    addPerson,
    removePerson,
    updatePersonName,
    
    // Métodos de gestión de items
    addItemToActivePerson,
    addItemToPerson,
    removeItemFromPerson,
    increaseItemQuantity,
    decreaseItemQuantity,
    
    // Métodos de cálculo
    getAllItems,
    getTotalItemsCount,
    getTotalAmount,
    getPersonTotal,
    
    // Métodos de control
    reset,
    toggleMultipleDiners,
    loadPersonsFromOrder
  };
}
