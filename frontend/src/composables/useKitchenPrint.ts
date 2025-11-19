import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

export function useKitchenPrint() {
  const authStore = useAuthStore();
  const isPrinting = ref(false);

  /**
   * Check if kitchen printing is enabled for current restaurant
   */
  const isPrintEnabled = () => {
    return authStore.restaurant?.kitchen_print_enabled ?? false;
  };

  /**
   * Build HTML for kitchen ticket
   * Single source of truth for ticket styling
   */
  const buildTicketHTML = (order: any, paperWidth: number): string => {
    const formatTime = (dateString: string) => {
      const date = new Date(dateString);
      return date.toLocaleTimeString('es-MX', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    };


    const getOrderTypeLabel = (type: string) => {
      const labels: Record<string, string> = {
        'dine_in': 'PARA COMER AQUÍ',
        'takeout': 'PARA LLEVAR',
        'delivery': 'DOMICILIO'
      };
      return labels[type] || type.toUpperCase();
    };

    // Helper function to build item HTML
    const buildItemHTML = (item: any) => {
      const itemName = item.menu_item?.name || item.menu_item_name || item.name || 'Item';
      const variantName = item.variant?.name || item.variant_name;
      const categoryName = item.menu_item?.category && typeof item.menu_item.category === 'object' 
        ? item.menu_item.category.name 
        : typeof item.menu_item?.category === 'string' 
          ? item.menu_item.category 
          : '';
      
      return `
      <div class="ticket-item">
        <div class="item-header">
          <span class="item-quantity">${item.quantity}x</span>
          <span class="item-name">${itemName}</span>
        </div>
        ${categoryName ? `
          <div class="item-category">${categoryName}</div>
        ` : ''}
        ${variantName ? `
          <div class="item-variant">${variantName}</div>
        ` : ''}
        ${item.special_instructions ? `
          <div class="item-notes">
            <span class="notes-text">${item.special_instructions}</span>
          </div>
        ` : ''}
      </div>
      `;
    };

    // Build items HTML - group by person if persons exist
    let itemsHTML = '';
    
    if (order.persons && order.persons.length > 0) {
      // Group items by person
      itemsHTML = order.persons.map((person: any, index: number) => {
        const personItems = order.items.filter((item: any) => item.person_id === person.id);
        if (personItems.length === 0) return '';
        
        const personName = person.name || `Persona ${index + 1}`;
        const personItemsHTML = personItems.map(buildItemHTML).join('');
        
        return `
        <div class="person-section">
          <div class="person-header">
            <strong>${personName}</strong>
          </div>
          ${personItemsHTML}
        </div>
        `;
      }).join('');
    } else {
      // No persons - show all items normally
      itemsHTML = order.items.map(buildItemHTML).join('');
    }

    const sizeClass = paperWidth === 58 ? 'ticket-58mm' : 'ticket-80mm';

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Ticket Cocina - Orden #${order.order_number}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Courier New', monospace;
      background: white;
      color: black;
      width: ${paperWidth-8}mm;
      margin: 0;
      padding: 2px 0;
    }

    .ticket-header {
      text-align: center;
      margin-bottom: 2px;
      padding: 0;
    }

    .order-number {
      font-size: 20px;
      font-weight: bold;
      margin-bottom: 1px;
    }

    .order-time {
      font-size: 14px;
    }

    .ticket-table {
      text-align: center;
      margin: 2px 0;
    }

    .table-number,
    .order-type {
      font-size: 18px;
      font-weight: bold;
      padding: 4px 0;
      background: transparent;
      color: black;
      display: inline-block;
    }

    .ticket-divider {
      border-top: 2px dashed black;
      margin: 2px 0;
    }

    .ticket-items {
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

    .ticket-item {
      margin-bottom: 4px;
      page-break-inside: avoid;
    }

    .item-header {
      display: flex;
      gap: 8px;
      margin-bottom: 1px;
    }

    .item-quantity {
      font-size: 22px;
      font-weight: bold;
      min-width: 28px;
    }

    .item-name {
      font-size: 20px;
      font-weight: bold;
      flex: 1;
      line-height: 1.2;
    }

    .item-category {
      font-size: 15px;
      margin-left: 8px;
      margin-bottom: 2px;
      color: black;
      text-transform: uppercase;
      font-weight: bold;
    }

    .item-variant {
      font-size: 16px;
      margin-left: 8px;
      margin-bottom: 2px;
      font-style: normal;
      font-weight: bold;
      color: black;
    }

    .item-notes {
      font-size: 15px;
      margin-left: 8px;
      margin-top: 4px;
      padding: 0;
      background: transparent;
      border: none;
      line-height: 1.4;
      color: black;
    }

    .item-notes strong {
      display: block;
      margin-bottom: 2px;
      font-size: 14px;
      font-weight: bold;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .notes-text {
      font-size: 16px;
      font-weight: 600;
      line-height: 1.3;
    }

    /* 58mm adjustments */
    .ticket-58mm .order-number {
      font-size: 18px;
    }

    .ticket-58mm .order-time {
      font-size: 12px;
    }

    .ticket-58mm .table-number,
    .ticket-58mm .order-type {
      font-size: 16px;
      padding: 4px 0;
    }

    .ticket-58mm .person-header {
      font-size: 14px;
    }

    .ticket-58mm .item-quantity {
      font-size: 20px;
      min-width: 28px;
    }

    .ticket-58mm .item-name {
      font-size: 18px;
    }

    .ticket-58mm .item-category {
      font-size: 13px;
      margin-left: 8px;
      color: black;
      font-weight: bold;
    }

    .ticket-58mm .item-variant {
      font-size: 14px;
      margin-left: 8px;
      font-weight: bold;
      color: black;
    }

    .ticket-58mm .item-notes {
      font-size: 13px;
      margin-left: 8px;
    }

    .ticket-58mm .item-notes strong {
      font-size: 12px;
    }

    .ticket-58mm .notes-text {
      font-size: 14px;
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
  </style>
</head>
<body class="${sizeClass}">
  <div class="ticket-header">
    <div class="order-number">ORDEN #${order.order_number}</div>
    <div class="order-time">${formatTime(order.created_at)}</div>
  </div>

  <div class="ticket-table">
    ${order.table_number 
      ? `<span class="table-number">MESA ${order.table_number}</span>`
      : order.customer_name 
        ? `<span class="order-type">${order.customer_name}</span>`
        : `<span class="order-type">${getOrderTypeLabel(order.order_type)}</span>`
    }
  </div>

  <div class="ticket-divider"></div>

  <div class="ticket-items">
    ${itemsHTML}
  </div>

  <div class="ticket-divider"></div>
</body>
</html>
    `;
  };

  /**
   * Print a kitchen ticket for an order
   * Opens the ticket in a new window and triggers print dialog
   */
  const printKitchenTicket = async (order: any) => {
    console.log('🖨️ printKitchenTicket called with order:', order);
    
    if (!isPrintEnabled()) {
      console.warn('⚠️ Kitchen printing is disabled for this restaurant');
      return;
    }

    console.log('✅ Kitchen printing is enabled, proceeding...');
    isPrinting.value = true;

    try {
      // Create a new window for printing
      console.log('📄 Opening print window...');
      const printWindow = window.open('', '_blank', 'width=800,height=600');
      
      if (!printWindow) {
        throw new Error('No se pudo abrir la ventana de impresión. Verifica que los pop-ups estén habilitados.');
      }

      console.log('✅ Print window opened');

      // Get paper width from restaurant settings
      const paperWidth = authStore.restaurant?.kitchen_print_paper_width || 80;
      console.log('📏 Paper width:', paperWidth);

      // Build the ticket HTML directly (simpler and more reliable)
      const ticketHTML = buildTicketHTML(order, paperWidth);
      console.log('📝 Ticket HTML generated, length:', ticketHTML.length);

      // Write HTML to print window
      printWindow.document.write(ticketHTML);
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
          };
        }, 250);
      };
    } catch (error) {
      console.error('❌ Error printing kitchen ticket:', error);
      throw error;
    } finally {
      isPrinting.value = false;
    }
  };

  return {
    isPrinting,
    isPrintEnabled,
    printKitchenTicket
  };
}
