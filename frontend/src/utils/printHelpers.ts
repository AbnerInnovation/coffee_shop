/**
 * Shared printing utilities for kitchen tickets, customer receipts, and pre-bills
 * Single source of truth for print formatting and HTML generation
 */

/**
 * Format date/time for tickets
 */
export const formatTime = (dateString: string, includeDate = false): string => {
  const date = new Date(dateString);
  
  if (includeDate) {
    return date.toLocaleString('es-MX', { 
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  }
  
  return date.toLocaleTimeString('es-MX', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true 
  });
};

/**
 * Format currency for display
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN'
  }).format(amount);
};

/**
 * Get translated order type label
 */
export const getOrderTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    'dine_in': 'Para Comer Aquí',
    'takeout': 'Para Llevar',
    'delivery': 'Domicilio'
  };
  return labels[type] || type;
};

/**
 * Get translated payment method label
 */
export const getPaymentMethodLabel = (method: string): string => {
  const labels: Record<string, string> = {
    'cash': 'Efectivo',
    'card': 'Tarjeta',
    'transfer': 'Transferencia',
    'other': 'Otro'
  };
  return labels[method] || method;
};

/**
 * Extract item data from order item (handles different data structures)
 */
export const extractItemData = (item: any) => {
  const itemName = item.menu_item?.name || item.menu_item_name || item.name || 'Item';
  const variantName = item.variant?.name || item.variant_name;
  const categoryName = item.menu_item?.category && typeof item.menu_item.category === 'object' 
    ? item.menu_item.category.name 
    : typeof item.menu_item?.category === 'string' 
      ? item.menu_item.category 
      : '';
  const unitPrice = item.unit_price || item.price || 0;
  const quantity = item.quantity || 1;
  const specialInstructions = item.special_instructions;
  
  return {
    itemName,
    variantName,
    categoryName,
    unitPrice,
    quantity,
    specialInstructions,
    subtotal: unitPrice * quantity
  };
};

/**
 * Build items HTML grouped by person
 * Returns object with HTML and metadata
 */
export interface GroupedItemsResult {
  html: string;
  hasPersons: boolean;
  itemsCount: number;
}

export const buildGroupedItemsHTML = (
  order: any,
  buildItemHTML: (item: any) => string
): GroupedItemsResult => {
  let html = '';
  let hasPersons = false;
  let itemsCount = 0;
  
  if (order.persons && order.persons.length > 0) {
    hasPersons = true;
    
    // Group items by person
    const groupedHTML = order.persons.map((person: any, index: number) => {
      const personItems = order.items?.filter((item: any) => item.person_id === person.id) || [];
      
      // Fallback: if no items have person_id, use items from person.items
      const items = personItems.length > 0 ? personItems : (person.items || []);
      
      if (items.length === 0) return '';
      
      itemsCount += items.length;
      const personName = person.name || `Persona ${index + 1}`;
      const personItemsHTML = items.map(buildItemHTML).join('');
      
      return `
      <div class="person-section">
        <div class="person-header">${personName}</div>
        ${personItemsHTML}
      </div>
      `;
    }).join('');
    
    // Check for orphan items (items without person_id)
    const orphanItems = order.items?.filter((item: any) => !item.person_id) || [];
    const orphanHTML = orphanItems.length > 0 
      ? orphanItems.map(buildItemHTML).join('') 
      : '';
    
    itemsCount += orphanItems.length;
    html = groupedHTML + orphanHTML;
    
    // Fallback: if no items were shown, show all items without grouping
    if (!html.trim() && order.items && order.items.length > 0) {
      console.warn('⚠️ No items matched any person, showing all items without grouping');
      html = order.items.map(buildItemHTML).join('');
      itemsCount = order.items.length;
      hasPersons = false;
    }
  } else {
    // No persons - show all items normally
    html = (order.items || []).map(buildItemHTML).join('');
    itemsCount = order.items?.length || 0;
  }
  
  return { html, hasPersons, itemsCount };
};

/**
 * Common CSS styles for all print tickets
 */
export const getCommonStyles = (paperWidth: number) => {
  return `
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Courier New', monospace;
      background: white;
      color: black;
      width: ${paperWidth - 8}mm;
      margin: 0;
      padding: 2px 0;
    }

    .divider {
      border-top: 2px dashed black;
      margin: 2px 0;
    }

    .person-section {
      margin-bottom: 8px;
      page-break-inside: avoid;
    }

    .person-header {
      font-size: 16px;
      font-weight: bold;
      text-align: center;
      padding: 4px 0;
      margin-bottom: 6px;
      border-top: 1px solid black;
      border-bottom: 1px solid black;
      background: transparent;
      color: black;
    }

    @media print {
      @page {
        margin: 0;
        size: ${paperWidth}mm auto;
      }

      body {
        margin: 0;
        padding: 2px 0;
      }
    }
  `;
};

/**
 * Get size-specific CSS class
 */
export const getSizeClass = (paperWidth: number): string => {
  return paperWidth === 58 ? 'ticket-58mm' : 'ticket-80mm';
};

/**
 * Calculate order totals
 */
export interface OrderTotals {
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
}

export const calculateOrderTotals = (order: any): OrderTotals => {
  const subtotal = order.subtotal || order.total_amount || 0;
  const discount = order.discount_amount || order.discount || 0;
  const tax = order.tax_amount || order.tax || 0;
  const total = order.total_amount || order.total || subtotal - discount + tax;
  
  return { subtotal, discount, tax, total };
};

/**
 * Open print window and trigger print dialog
 */
export const openPrintWindow = async (
  html: string,
  onComplete?: () => void
): Promise<void> => {
  console.log('📄 Opening print window...');
  const printWindow = window.open('', '_blank', 'width=800,height=600');
  
  if (!printWindow) {
    throw new Error('No se pudo abrir la ventana de impresión. Verifica que los pop-ups estén habilitados.');
  }

  console.log('✅ Print window opened');

  // Write HTML to print window
  printWindow.document.write(html);
  printWindow.document.close();
  console.log('✅ HTML written to print window');

  // Wait for content to load, then print
  printWindow.onload = () => {
    console.log('📄 Print window loaded, triggering print dialog...');
    setTimeout(() => {
      printWindow.print();
      console.log('🖨️ Print dialog triggered');
      printWindow.onafterprint = () => {
        console.log('✅ Print completed, closing window');
        printWindow.close();
        if (onComplete) onComplete();
      };
    }, 250);
  };
};
