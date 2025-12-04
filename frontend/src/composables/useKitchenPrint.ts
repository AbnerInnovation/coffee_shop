import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import {
  formatTime,
  getOrderTypeLabel,
  extractItemData,
  buildGroupedItemsHTML,
  getCommonStyles,
  getSizeClass,
  openPrintWindow
} from '@/utils/printHelpers';

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
    // Helper function to build item HTML for kitchen
    const buildItemHTML = (item: any) => {
      const { itemName, variantName, categoryName, quantity, specialInstructions } = extractItemData(item);
      
      return `
      <div class="ticket-item">
        <div class="item-header">
          <span class="item-quantity">${quantity}x</span>
          <span class="item-name">${itemName}</span>
        </div>
        ${categoryName ? `
          <div class="item-category">${categoryName}</div>
        ` : ''}
        ${variantName ? `
          <div class="item-variant">${variantName}</div>
        ` : ''}
        ${specialInstructions ? `
          <div class="item-notes">
            <span class="notes-text">${specialInstructions}</span>
          </div>
        ` : ''}
      </div>
      `;
    };

    // Build items HTML - group by person if persons exist
    const { html: itemsHTML } = buildGroupedItemsHTML(order, buildItemHTML);
    const sizeClass = getSizeClass(paperWidth);
    const commonStyles = getCommonStyles(paperWidth);

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Ticket Cocina - Orden #${order.order_number}</title>
  <style>
    ${commonStyles}

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

    /* Override person-header for kitchen (uppercase) */
    .person-header strong {
      text-transform: uppercase;
    }

    .ticket-items {
      margin: 2px 0;
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
      // Ensure restaurant data is loaded
      if (!authStore.restaurant) {
        console.log('📥 Loading restaurant data...');
        await authStore.loadRestaurant();
        console.log('✅ Restaurant data loaded:', authStore.restaurant?.name);
      }

      // Get paper width from restaurant settings
      const paperWidth = authStore.restaurant?.kitchen_print_paper_width || 80;
      console.log('📏 Paper width:', paperWidth);

      // Build the ticket HTML
      const ticketHTML = buildTicketHTML(order, paperWidth);
      console.log('📝 Ticket HTML generated, length:', ticketHTML.length);

      // Open print window and trigger print
      await openPrintWindow(ticketHTML);
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
