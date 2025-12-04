import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import {
  formatTime,
  formatCurrency,
  getOrderTypeLabel,
  getPaymentMethodLabel,
  extractItemData,
  buildGroupedItemsHTML,
  getCommonStyles,
  getSizeClass,
  calculateOrderTotals,
  openPrintWindow
} from '@/utils/printHelpers';

export function useCustomerPrint() {
  const authStore = useAuthStore();
  const isPrinting = ref(false);

  /**
   * Check if customer receipt printing is enabled for current restaurant
   */
  const isPrintEnabled = () => {
    return authStore.restaurant?.customer_print_enabled ?? true; // Enabled by default
  };

  /**
   * Build HTML for pre-bill (cuenta) - shows items and total, no payment info
   * Used when customer asks for the bill before paying
   */
  const buildPreBillHTML = (order: any, paperWidth: number): string => {
    const sizeClass = getSizeClass(paperWidth);
    const restaurant = authStore.restaurant;
    const commonStyles = getCommonStyles(paperWidth);

    // Debug: Log order and restaurant data
    console.log('🔍 Building pre-bill HTML for order:', {
      order_number: order.order_number,
      items_count: order.items?.length || 0,
      persons_count: order.persons?.length || 0,
      restaurant_name: restaurant?.name,
      restaurant_loaded: !!restaurant
    });

    // Helper function to build item HTML for pre-bill
    const buildItemHTML = (item: any) => {
      const { itemName, variantName, categoryName, subtotal } = extractItemData(item);
      
      return `
      <div class="item-row">
        <div class="item-main">
          <span class="item-qty">${item.quantity}x</span>
          <span class="item-name">${itemName}${variantName ? ` (${variantName})` : ''}</span>
        </div>
        <span class="item-price">${formatCurrency(subtotal)}</span>
      </div>
      ${categoryName ? `<div class="item-category">${categoryName}</div>` : ''}
      `;
    };

    // Build items HTML - group by person if persons exist
    const { html: itemsHTML } = buildGroupedItemsHTML(order, buildItemHTML);
    const { subtotal, discount, tax, total } = calculateOrderTotals(order);

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Pre-Cuenta - Orden #${order.order_number}</title>
  <style>
    ${commonStyles}

    body {
      padding: ${paperWidth === 58 ? '1mm 2mm 1mm 0' : '4mm 4mm 4mm 0'};
      font-weight: 600;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
      overflow: hidden;
    }

    .receipt-header {
      text-align: center;
      margin-bottom: 2mm;
      border-bottom: 2px solid black;
      padding-bottom: 1mm;
    }

    .restaurant-name {
      font-size: 16px;
      font-weight: 900;
      margin-bottom: 1mm;
      letter-spacing: 1px;
    }

    .restaurant-info {
      font-size: 11px;
      line-height: 1.4;
      font-weight: 600;
    }

    .bill-title {
      text-align: center;
      font-size: 18px;
      font-weight: 900;
      margin: 2mm 0;
      padding: 2mm 0;
      border-top: 3px double black;
      border-bottom: 3px double black;
      letter-spacing: 2px;
    }

    .order-info {
      font-size: 12px;
      margin-bottom: 2mm;
      line-height: 1.2;
      font-weight: 700;
    }

    .order-info-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5mm;
    }
    
    .order-info-row strong {
      font-weight: 900;
    }

    .divider {
      border-top: 1px dashed black;
      margin: 2mm 0;
    }

    /* Override person-header for pre-bill */
    .person-header {
      font-size: 13px;
      font-weight: 900;
      text-align: left;
      border-bottom: 2px solid black;
      letter-spacing: 0.5px;
    }

    .item-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1mm;
      margin-bottom: 0.5mm;
      page-break-inside: avoid;
    }

    .item-main {
      display: flex;
      align-items: flex-start;
      gap: 1mm;
      flex: 1;
    }

    .item-qty {
      font-size: 14px;
      font-weight: 900;
      min-width: 8mm;
      flex-shrink: 0;
    }

    .item-name {
      font-size: 13px;
      font-weight: 700;
      flex: 1;
      line-height: 1.1;
      word-wrap: break-word;
      overflow-wrap: break-word;
    }

    .item-price {
      font-size: 13px;
      font-weight: 900;
      text-align: right;
      white-space: nowrap;
      flex-shrink: 0;
      min-width: 15mm;
    }

    .item-category {
      font-size: 10px;
      font-weight: 900;
      color: #000;
      margin-left: 9mm;
      margin-bottom: 1mm;
      font-style: italic;
    }

    .totals-section {
      margin-top: 2mm;
      border-top: 2px solid black;
      padding-top: 2mm;
    }

    .total-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 1mm;
      font-size: 13px;
      font-weight: 700;
    }

    .total-row.final {
      font-size: 14px;
      font-weight: 900;
      margin-top: 1mm;
      padding-top: 1mm;
      border-top: 3px double black;
      letter-spacing: 0.5px;
    }

    .footer {
      text-align: center;
      margin-top: 2mm;
      padding-top: 2mm;
      border-top: 1px dashed black;
      font-size: 10px;
    }

    /* 58mm adjustments - balanced and readable */
    .receipt-58mm .receipt-header {
      margin-bottom: 1mm;
      padding-bottom: 1mm;
    }

    .receipt-58mm .restaurant-name {
      font-size: 13px;
      letter-spacing: 0.5px;
      margin-bottom: 1mm;
    }

    .receipt-58mm .restaurant-info {
      font-size: 9px;
    }

    .receipt-58mm .bill-title {
      font-size: 14px;
      margin: 1mm 0;
      padding: 1mm 0;
      letter-spacing: 1px;
    }

    .receipt-58mm .order-info {
      font-size: 10px;
      margin-bottom: 1mm;
      line-height: 1.2;
    }

    .receipt-58mm .order-info-row {
      margin-bottom: 0.5mm;
    }

    .receipt-58mm .divider {
      margin: 1.5mm 0;
    }

    .receipt-58mm .person-section {
      margin-bottom: 1.5mm;
    }

    .receipt-58mm .person-name {
      font-size: 12px;
      padding: 1mm 0;
      margin-bottom: 1mm;
    }

    .receipt-58mm .item-row {
      margin-bottom: 0.5mm;
      gap: 0.5mm;
    }

    .receipt-58mm .item-qty {
      font-size: 12px;
      min-width: 5mm;
    }

    .receipt-58mm .item-name {
      font-size: 11px;
      line-height: 1.1;
    }

    .receipt-58mm .item-price {
      font-size: 11px;
      min-width: 10mm;
    }

    .receipt-58mm .item-category {
      font-size: 9px;
      font-weight: 900;
      margin-left: 6mm;
      margin-bottom: 0.5mm;
    }

    .receipt-58mm .totals-section {
      margin-top: 1mm;
      padding-top: 1mm;
    }

    .receipt-58mm .total-row {
      font-size: 11px;
      margin-bottom: 0.5mm;
    }

    .receipt-58mm .total-row.final {
      font-size: 13px;
      margin-top: 1mm;
      padding-top: 1mm;
    }

    .receipt-58mm .footer {
      margin-top: 2mm;
      padding-top: 1mm;
      font-size: 9px;
    }

  </style>
</head>
<body class="${sizeClass}">
  <div class="receipt-header">
    <div class="restaurant-name">${restaurant?.name || 'Restaurante'}</div>
    <div class="restaurant-info">
      ${restaurant?.address ? `${restaurant.address}<br>` : ''}
      ${restaurant?.phone ? `Tel: ${restaurant.phone}<br>` : ''}
    </div>
  </div>

  <div class="bill-title">PRE-CUENTA</div>

  <div class="order-info">
    <div class="order-info-row">
      <span>Orden:</span>
      <span><strong>#${order.order_number}</strong></span>
    </div>
    <div class="order-info-row">
      <span>Fecha:</span>
      <span>${formatTime(order.created_at, true)}</span>
    </div>
    ${order.table_number ? `
    <div class="order-info-row">
      <span>Mesa:</span>
      <span><strong>${order.table_number}</strong></span>
    </div>
    ` : ''}
    ${order.customer_name ? `
    <div class="order-info-row">
      <span>Cliente:</span>
      <span>${order.customer_name}</span>
    </div>
    ` : ''}
    ${order.waiter?.name ? `
    <div class="order-info-row">
      <span>Atendió:</span>
      <span>${order.waiter.name}</span>
    </div>
    ` : ''}
    <div class="order-info-row">
      <span>Tipo:</span>
      <span>${getOrderTypeLabel(order.order_type)}</span>
    </div>
  </div>

  <div class="divider"></div>

  <div class="items-section">
    ${itemsHTML}
  </div>

  <div class="totals-section">
    <div class="total-row">
      <span>Subtotal:</span>
      <span>${formatCurrency(subtotal)}</span>
    </div>
    ${discount > 0 ? `
    <div class="total-row">
      <span>Descuento:</span>
      <span>-${formatCurrency(discount)}</span>
    </div>
    ` : ''}
    ${tax > 0 ? `
    <div class="total-row">
      <span>IVA:</span>
      <span>${formatCurrency(tax)}</span>
    </div>
    ` : ''}
    <div class="total-row final">
      <span>TOTAL:</span>
      <span>${formatCurrency(total)}</span>
    </div>
  </div>

  <div class="footer">
    Este no es un comprobante de pago<br>
    Solicite su ticket fiscal al realizar el pago
  </div>
</body>
</html>
    `;
  };

  /**
   * Build HTML for customer receipt (after payment)
   * Single source of truth for receipt styling
   */
  const buildReceiptHTML = (order: any, paperWidth: number): string => {
    const sizeClass = getSizeClass(paperWidth);
    const commonStyles = getCommonStyles(paperWidth);

    // Helper function to build item HTML for receipt (table format)
    const buildItemHTML = (item: any) => {
      const { itemName, variantName, categoryName, quantity, subtotal } = extractItemData(item);
      
      return `
      <tr class="receipt-item">
        <td class="item-quantity">${quantity}</td>
        <td class="item-description">
          <div class="item-name">${itemName}${variantName ? ` (${variantName})` : ''}</div>
          ${categoryName ? `<div class="item-category">${categoryName}</div>` : ''}
        </td>
        <td class="item-total">${formatCurrency(subtotal)}</td>
      </tr>
      `;
    };

    // Build items HTML - group by person if persons exist
    console.log('🔍 Building receipt HTML - order data:', {
      has_persons: !!(order.persons && order.persons.length > 0),
      persons_count: order.persons?.length || 0,
      items_count: order.items?.length || 0
    });
    
    // For table format, we need to wrap person sections in table rows
    const buildPersonSection = (personName: string, itemsHTML: string) => `
      <tr class="person-section">
        <td colspan="3" class="person-header">${personName}</td>
      </tr>
      ${itemsHTML}
    `;
    
    let itemsHTML = '';
    if (order.persons && order.persons.length > 0) {
      itemsHTML = order.persons.map((person: any, index: number) => {
        const personItems = order.items?.filter((item: any) => item.person_id === person.id) || [];
        const items = personItems.length > 0 ? personItems : (person.items || []);
        if (items.length === 0) return '';
        
        const personName = person.name || `Persona ${index + 1}`;
        const personItemsHTML = items.map(buildItemHTML).join('');
        return buildPersonSection(personName, personItemsHTML);
      }).join('');
      
      if (!itemsHTML && order.items && order.items.length > 0) {
        console.log('⚠️ No items matched persons, showing all items');
        itemsHTML = order.items.map(buildItemHTML).join('');
      }
    } else {
      itemsHTML = (order.items || []).map(buildItemHTML).join('');
    }

    // Calculate totals
    const { subtotal, discount, tax, total } = calculateOrderTotals(order);
    const restaurantName = authStore.restaurant?.name || 'Restaurante';
    const restaurantAddress = authStore.restaurant?.address || '';
    const restaurantPhone = authStore.restaurant?.phone || '';
    const restaurantEmail = authStore.restaurant?.email || '';

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Ticket - Orden #${order.order_number}</title>
  <style>
    ${commonStyles}

    body {
      padding: 4px;
      font-size: 12px;
      font-weight: 700;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    .receipt-header {
      text-align: center;
      margin-bottom: 8px;
      padding-bottom: 8px;
      border-bottom: 2px solid black;
    }

    .restaurant-name {
      font-size: 18px;
      font-weight: 900;
      margin-bottom: 4px;
    }

    .restaurant-info {
      font-size: 11px;
      line-height: 1.4;
    }

    .receipt-info {
      margin: 8px 0;
      font-size: 11px;
    }

    .receipt-info-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 2px;
    }

    .receipt-divider {
      border-top: 1px dashed black;
      margin: 8px 0;
    }

    .receipt-items {
      margin: 8px 0;
    }

    .items-table {
      width: 100%;
      border-collapse: collapse;
    }

    .items-table th {
      text-align: left;
      font-size: 11px;
      font-weight: 900;
      padding: 4px 2px;
      border-bottom: 1px solid black;
    }

    .items-table th.text-right {
      text-align: right;
    }

    .receipt-item td {
      padding: 4px 2px;
      vertical-align: top;
      font-size: 11px;
    }

    .item-quantity {
      width: 15%;
      text-align: center;
      font-weight: 900;
    }

    .item-description {
      width: 65%;
    }

    .item-name {
      font-weight: 900;
      margin-bottom: 2px;
    }

    .item-category {
      font-size: 10px;
      font-weight: bold;
      color: #666;
      margin-top: 1px;
    }

    .item-total {
      text-align: right;
      width: 20%;
      font-weight: 900;
    }

    .person-section td {
      padding: 6px 2px 4px 2px;
    }

    .person-header {
      font-weight: 900;
      font-size: 12px;
      text-align: center;
      background: #f0f0f0;
      border-top: 1px solid black;
      border-bottom: 1px solid black;
    }

    .receipt-totals {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid black;
    }

    .total-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      font-size: 12px;
      font-weight: 700;
    }

    .total-row.grand-total {
      font-size: 16px;
      font-weight: 900;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 2px solid black;
    }

    .receipt-payment {
      margin-top: 12px;
      padding-top: 8px;
      border-top: 1px dashed black;
    }

    .payment-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      font-size: 12px;
      font-weight: 700;
    }

    .payment-row.change {
      font-weight: 900;
      margin-top: 4px;
    }

    .receipt-footer {
      text-align: center;
      margin-top: 16px;
      padding-top: 8px;
      border-top: 2px solid black;
      font-size: 11px;
    }

    .footer-message {
      margin-top: 8px;
      font-weight: 900;
    }

    /* 58mm adjustments */
    .receipt-58mm {
      font-size: 11px;
    }

    .receipt-58mm .restaurant-name {
      font-size: 16px;
    }

    .receipt-58mm .restaurant-info {
      font-size: 10px;
    }

    .receipt-58mm .items-table th,
    .receipt-58mm .receipt-item td {
      font-size: 10px;
    }

    .receipt-58mm .item-variant,
    .receipt-58mm .item-notes {
      font-size: 9px;
    }

    .receipt-58mm .total-row {
      font-size: 11px;
    }

    .receipt-58mm .total-row.grand-total {
      font-size: 14px;
    }
  </style>
</head>
<body class="${sizeClass}">
  <div class="receipt-header">
    <div class="restaurant-name">${restaurantName}</div>
    ${restaurantAddress ? `<div class="restaurant-info">${restaurantAddress}</div>` : ''}
    ${restaurantPhone ? `<div class="restaurant-info">Tel: ${restaurantPhone}</div>` : ''}
  </div>

  <div class="receipt-divider"></div>

  <div class="receipt-info">
    <div class="receipt-info-row">
      <span><strong>Folio:</strong> #${order.order_number}</span>
      <span><strong>Fecha:</strong> ${formatTime(order.created_at, true).split(',')[0]}</span>
    </div>
    <div class="receipt-info-row">
      <span><strong>Hora:</strong> ${formatTime(order.created_at, true).split(',')[1]?.trim() || ''}</span>
    </div>
    ${order.table_number ? `
    <div class="receipt-info-row">
      <span><strong>Mesa:</strong> ${order.table_number}</span>
      <span><strong>Tipo:</strong> ${getOrderTypeLabel(order.order_type)}</span>
    </div>
    ` : `
    <div class="receipt-info-row">
      <span><strong>Tipo:</strong> ${getOrderTypeLabel(order.order_type)}</span>
      ${order.customer_name ? `<span><strong>Cliente:</strong> ${order.customer_name}</span>` : ''}
    </div>
    `}
    ${order.waiter_name ? `
    <div class="receipt-info-row">
      <span><strong>Atendió:</strong> ${order.waiter_name}</span>
    </div>
    ` : ''}
  </div>

  <div class="receipt-divider"></div>

  <div class="receipt-items">
    <table class="items-table">
      <thead>
        <tr>
          <th>Cant.</th>
          <th>Desc.</th>
          <th class="text-right">Total</th>
        </tr>
      </thead>
      <tbody>
        ${itemsHTML}
      </tbody>
    </table>
  </div>

  <div class="receipt-totals">
    <div class="total-row">
      <span>Subtotal:</span>
      <span>${formatCurrency(subtotal)}</span>
    </div>
    ${discount > 0 ? `
    <div class="total-row">
      <span>Descuento:</span>
      <span>-${formatCurrency(discount)}</span>
    </div>
    ` : ''}
    ${tax > 0 ? `
    <div class="total-row">
      <span>IVA:</span>
      <span>${formatCurrency(tax)}</span>
    </div>
    ` : ''}
    <div class="total-row grand-total">
      <span>TOTAL:</span>
      <span>${formatCurrency(total)}</span>
    </div>
  </div>

  ${order.payment_method ? `
  <div class="receipt-payment">
    <div class="payment-row">
      <span><strong>Método de Pago:</strong></span>
      <span>${getPaymentMethodLabel(order.payment_method)}</span>
    </div>
    ${order.payment_method === 'cash' && order.amount_paid ? `
    <div class="payment-row">
      <span>Pagó con:</span>
      <span>${formatCurrency(order.amount_paid)}</span>
    </div>
    <div class="payment-row change">
      <span>Cambio:</span>
      <span>${formatCurrency(order.amount_paid - total)}</span>
    </div>
    ` : ''}
  </div>
  ` : ''}

  <div class="receipt-divider"></div>

  <div class="receipt-footer">
    <div class="footer-message">¡Gracias por su preferencia!</div>
    <div class="footer-message">¡Vuelva pronto!</div>
    <div style="margin-top: 8px; font-size: 9px;">
      Este ticket no es un comprobante fiscal
    </div>
  </div>
</body>
</html>
    `;
  };

  /**
   * Print a customer receipt for an order
   * Opens the receipt in a new window and triggers print dialog
   */
  const printCustomerReceipt = async (order: any) => {
    console.log('🖨️ printCustomerReceipt called with order:', order);
    
    if (!isPrintEnabled()) {
      console.warn('⚠️ Customer receipt printing is disabled for this restaurant');
      return;
    }

    console.log('✅ Customer receipt printing is enabled, proceeding...');
    isPrinting.value = true;

    try {
      // Ensure restaurant data is loaded
      if (!authStore.restaurant) {
        console.log('📥 Loading restaurant data...');
        await authStore.loadRestaurant();
        console.log('✅ Restaurant data loaded:', authStore.restaurant?.name);
      }

      // Get paper width from restaurant settings
      const paperWidth = authStore.restaurant?.customer_print_paper_width || 80;
      console.log('📏 Paper width:', paperWidth);

      // Build the receipt HTML
      const receiptHTML = buildReceiptHTML(order, paperWidth);
      console.log('📝 Receipt HTML generated, length:', receiptHTML.length);

      // Open print window and trigger print
      await openPrintWindow(receiptHTML);
    } catch (error) {
      console.error('❌ Error printing customer receipt:', error);
      throw error;
    } finally {
      isPrinting.value = false;
    }
  };

  /**
   * Print a pre-bill (cuenta) for an order
   * Opens the pre-bill in a new window and triggers print dialog
   * Used when customer asks for the bill before paying
   */
  const printPreBill = async (order: any) => {
    console.log('🖨️ printPreBill called with order:', order);
    
    if (!isPrintEnabled()) {
      console.warn('⚠️ Customer printing is disabled for this restaurant');
      return;
    }

    console.log('✅ Customer printing is enabled, proceeding with pre-bill...');
    isPrinting.value = true;

    try {
      // Ensure restaurant data is loaded
      if (!authStore.restaurant) {
        console.log('📥 Loading restaurant data...');
        await authStore.loadRestaurant();
        console.log('✅ Restaurant data loaded:', authStore.restaurant?.name);
      }

      // Get paper width from restaurant settings
      const paperWidth = authStore.restaurant?.customer_print_paper_width || 80;
      console.log('📏 Paper width:', paperWidth);

      // Build the pre-bill HTML
      const preBillHTML = buildPreBillHTML(order, paperWidth);
      console.log('📝 Pre-bill HTML generated, length:', preBillHTML.length);

      // Open print window and trigger print
      await openPrintWindow(preBillHTML);
    } catch (error) {
      console.error('❌ Error printing pre-bill:', error);
      throw error;
    } finally {
      isPrinting.value = false;
    }
  };

  return {
    isPrinting,
    isPrintEnabled,
    printPreBill,
    printCustomerReceipt
  };
}
