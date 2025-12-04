import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

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
   * Format currency for display
   */
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(amount);
  };

  /**
   * Build HTML for pre-bill (cuenta) - shows items and total, no payment info
   * Used when customer asks for the bill before paying
   */
  const buildPreBillHTML = (order: any, paperWidth: number): string => {
    const formatTime = (dateString: string) => {
      const date = new Date(dateString);
      return date.toLocaleString('es-MX', { 
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    };

    const getOrderTypeLabel = (type: string) => {
      const labels: Record<string, string> = {
        'dine_in': 'Para Comer Aquí',
        'takeout': 'Para Llevar',
        'delivery': 'Domicilio'
      };
      return labels[type] || type;
    };

    const sizeClass = paperWidth === 58 ? 'receipt-58mm' : 'receipt-80mm';
    const restaurant = authStore.restaurant;

    // Debug: Log order and restaurant data
    console.log('🔍 Building pre-bill HTML for order:', {
      order_number: order.order_number,
      items_count: order.items?.length || 0,
      persons_count: order.persons?.length || 0,
      restaurant_name: restaurant?.name,
      restaurant_loaded: !!restaurant
    });

    // Helper function to build item HTML (same pattern as kitchen ticket)
    const buildItemHTML = (item: any) => {
      const itemName = item.menu_item?.name || item.menu_item_name || item.name || 'Item';
      const variantName = item.variant?.name || item.variant_name;
      const categoryName = item.menu_item?.category && typeof item.menu_item.category === 'object' 
        ? item.menu_item.category.name 
        : typeof item.menu_item?.category === 'string' 
          ? item.menu_item.category 
          : '';
      const unitPrice = item.unit_price || item.price || 0;
      const itemTotal = item.quantity * unitPrice;
      
      return `
      <div class="item-row">
        <div class="item-main">
          <span class="item-qty">${item.quantity}x</span>
          <span class="item-name">${itemName}${variantName ? ` (${variantName})` : ''}</span>
        </div>
        <span class="item-price">${formatCurrency(itemTotal)}</span>
      </div>
      ${categoryName ? `<div class="item-category">${categoryName}</div>` : ''}
      `;
    };

    // Build items HTML - group by person if persons exist (same pattern as kitchen ticket)
    let itemsHTML = '';
    
    if (order.persons && order.persons.length > 0) {
      // Group items by person
      const groupedHTML = order.persons.map((person: any, index: number) => {
        const personItems = order.items.filter((item: any) => item.person_id === person.id);
        if (personItems.length === 0) return '';
        
        const personName = person.name || `Persona ${index + 1}`;
        const personItemsHTML = personItems.map(buildItemHTML).join('');
        
        return `
        <div class="person-section">
          <div class="person-name">${personName}</div>
          ${personItemsHTML}
        </div>
        `;
      }).join('');
      
      // Check if there are items without person_id (orphan items)
      const orphanItems = order.items.filter((item: any) => !item.person_id);
      const orphanHTML = orphanItems.length > 0 
        ? orphanItems.map(buildItemHTML).join('') 
        : '';
      
      // Combine grouped and orphan items
      itemsHTML = groupedHTML + orphanHTML;
      
      // If no items were shown at all, show all items without grouping
      if (!itemsHTML.trim()) {
        console.warn('⚠️ No items matched any person, showing all items without grouping');
        itemsHTML = order.items.map(buildItemHTML).join('');
      }
    } else {
      // No persons - show all items normally
      itemsHTML = order.items.map(buildItemHTML).join('');
    }

    const subtotal = order.subtotal || 0;
    const discount = order.discount || 0;
    const tax = order.tax || 0;
    const total = order.total || subtotal - discount + tax;

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Pre-Cuenta - Orden #${order.order_number}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Courier New', monospace;
      background: white;
      color: #000;
      width: ${paperWidth - 8}mm;
      max-width: ${paperWidth - 8}mm;
      margin: 0;
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

    .person-section {
      margin-bottom: 2mm;
    }

    .person-name {
      font-size: 13px;
      font-weight: 900;
      margin-bottom: 1mm;
      padding: 1mm 0;
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

    @media print {
      @page {
        margin: 0;
        size: ${paperWidth}mm auto;
      }

      body {
        margin: 0;
        padding: 4mm;
      }
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
      <span>${formatTime(order.created_at)}</span>
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
    const formatTime = (dateString: string) => {
      const date = new Date(dateString);
      return date.toLocaleString('es-MX', { 
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
      });
    };

    const getOrderTypeLabel = (type: string) => {
      const labels: Record<string, string> = {
        'dine_in': 'Para Comer Aquí',
        'takeout': 'Para Llevar',
        'delivery': 'Domicilio'
      };
      return labels[type] || type;
    };

    const getPaymentMethodLabel = (method: string) => {
      const labels: Record<string, string> = {
        'cash': 'Efectivo',
        'card': 'Tarjeta',
        'transfer': 'Transferencia',
        'other': 'Otro'
      };
      return labels[method] || method;
    };

    // Helper function to build item HTML
    const buildItemHTML = (item: any) => {
      const itemName = item.menu_item?.name || item.menu_item_name || item.name || 'Item';
      const variantName = item.variant?.name || item.variant_name;
      const unitPrice = item.unit_price || item.price || 0;
      const quantity = item.quantity || 1;
      const subtotal = unitPrice * quantity;
      
      return `
      <tr class="receipt-item">
        <td class="item-quantity">${quantity}</td>
        <td class="item-description">
          <div class="item-name">${itemName}</div>
          ${variantName ? `<div class="item-variant">${variantName}</div>` : ''}
          ${item.special_instructions ? `<div class="item-notes">${item.special_instructions}</div>` : ''}
        </td>
        <td class="item-price">${formatCurrency(unitPrice)}</td>
        <td class="item-total">${formatCurrency(subtotal)}</td>
      </tr>
      `;
    };

    // Build items HTML - group by person if persons exist
    let itemsHTML = '';
    
    console.log('🔍 Building receipt HTML - order data:', {
      has_persons: !!(order.persons && order.persons.length > 0),
      persons_count: order.persons?.length || 0,
      items_count: order.items?.length || 0
    });
    
    if (order.persons && order.persons.length > 0) {
      // Group items by person
      itemsHTML = order.persons.map((person: any, index: number) => {
        const personItems = order.items?.filter((item: any) => item.person_id === person.id) || [];
        
        // Fallback: if no items have person_id, use items from person.items
        const items = personItems.length > 0 ? personItems : (person.items || []);
        
        if (items.length === 0) return '';
        
        const personName = person.name || `Persona ${index + 1}`;
        const personItemsHTML = items.map(buildItemHTML).join('');
        
        return `
        <tr class="person-section">
          <td colspan="4" class="person-header">${personName}</td>
        </tr>
        ${personItemsHTML}
        `;
      }).join('');
      
      // Fallback: if no items matched persons, show all items
      if (!itemsHTML && order.items && order.items.length > 0) {
        console.log('⚠️ No items matched persons, showing all items');
        itemsHTML = order.items.map(buildItemHTML).join('');
      }
    } else {
      // No persons - show all items normally
      itemsHTML = (order.items || []).map(buildItemHTML).join('');
    }

    // Calculate totals
    const subtotal = order.subtotal || order.total_amount || 0;
    const discount = order.discount_amount || 0;
    const tax = order.tax_amount || 0;
    const total = order.total_amount || 0;

    const sizeClass = paperWidth === 58 ? 'receipt-58mm' : 'receipt-80mm';
    const restaurantName = authStore.restaurant?.name || 'Restaurante';
    const restaurantAddress = authStore.restaurant?.address || '';
    const restaurantPhone = authStore.restaurant?.phone || '';

    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Ticket - Orden #${order.order_number}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Courier New', monospace;
      background: white;
      color: #000;
      width: ${paperWidth-8}mm;
      margin: 0;
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
      width: 45%;
    }

    .item-name {
      font-weight: 900;
      margin-bottom: 2px;
    }

    .item-variant {
      font-size: 10px;
      font-style: italic;
      margin-bottom: 2px;
    }

    .item-notes {
      font-size: 10px;
      color: #333;
      margin-top: 2px;
    }

    .item-price,
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

    @media print {
      @page {
        margin: 0;
        size: ${paperWidth}mm auto;
      }

      body {
        margin: 0;
        padding: 4px;
      }
    }
  </style>
</head>
<body class="${sizeClass}">
  <div class="receipt-header">
    <div class="restaurant-name">${restaurantName}</div>
    ${restaurantAddress ? `<div class="restaurant-info">${restaurantAddress}</div>` : ''}
    ${restaurantPhone ? `<div class="restaurant-info">Tel: ${restaurantPhone}</div>` : ''}
  </div>

  <div class="receipt-info">
    <div class="receipt-info-row">
      <span><strong>Orden:</strong> #${order.order_number}</span>
      <span><strong>Fecha:</strong> ${formatTime(order.created_at)}</span>
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
          <th class="text-right">Precio</th>
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

  <div class="receipt-footer">
    <div>¡Gracias por su preferencia!</div>
    <div class="footer-message">¡Vuelva pronto!</div>
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

      // Create a new window for printing
      console.log('📄 Opening print window...');
      const printWindow = window.open('', '_blank', 'width=800,height=600');
      
      if (!printWindow) {
        throw new Error('No se pudo abrir la ventana de impresión. Verifica que los pop-ups estén habilitados.');
      }

      console.log('✅ Print window opened');

      // Get paper width from restaurant settings
      const paperWidth = authStore.restaurant?.customer_print_paper_width || 80;
      console.log('📏 Paper width:', paperWidth);

      // Build the receipt HTML
      const receiptHTML = buildReceiptHTML(order, paperWidth);
      console.log('📝 Receipt HTML generated, length:', receiptHTML.length);

      // Write HTML to print window
      printWindow.document.write(receiptHTML);
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

      // Create a new window for printing
      console.log('📄 Opening print window for pre-bill...');
      const printWindow = window.open('', '_blank', 'width=800,height=600');
      
      if (!printWindow) {
        throw new Error('No se pudo abrir la ventana de impresión. Verifica que los pop-ups estén habilitados.');
      }

      console.log('✅ Print window opened');

      // Get paper width from restaurant settings
      const paperWidth = authStore.restaurant?.customer_print_paper_width || 80;
      console.log('📏 Paper width:', paperWidth);

      // Build the pre-bill HTML
      const preBillHTML = buildPreBillHTML(order, paperWidth);
      console.log('📝 Pre-bill HTML generated, length:', preBillHTML.length);

      // Write HTML to print window
      printWindow.document.write(preBillHTML);
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
