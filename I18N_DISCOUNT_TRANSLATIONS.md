# Discount Price Feature - i18n Translations

## Overview
All discount price UI elements now support internationalization (i18n) with English and Spanish translations.

## Translation Keys Added

### English (`en.json`)
```json
{
  "app": {
    "forms": {
      "variant": {
        "discount_price": "Discount Price"
      },
      "discount_price": "Discount Price (Optional)",
      "discount_price_help": "When set, this price will be used instead of the regular price",
      "discount_active": "Discount Active",
      "customers_save": "Customers save: {amount}",
      "sale_badge": "Sale",
      "save_badge": "Save {amount}",
      "discount_placeholder": "Leave empty for no discount"
    }
  }
}
```

### Spanish (`es.json`)
```json
{
  "app": {
    "forms": {
      "variant": {
        "discount_price": "Precio de descuento"
      },
      "discount_price": "Precio de Descuento (Opcional)",
      "discount_price_help": "Cuando se establece, este precio se usará en lugar del precio regular",
      "discount_active": "Descuento Activo",
      "customers_save": "Los clientes ahorran: {amount}",
      "sale_badge": "Oferta",
      "save_badge": "Ahorra {amount}",
      "discount_placeholder": "Dejar vacío para no aplicar descuento"
    }
  }
}
```

## Components Updated

### 1. MenuItemForm.vue
- **Discount price label**: `{{ t('app.forms.discount_price') }}`
- **Placeholder**: `{{ t('app.forms.discount_placeholder') }}`
- **Help text**: `{{ t('app.forms.discount_price_help') }}`
- **Discount active badge**: `{{ t('app.forms.discount_active') }}`
- **Savings message**: `{{ t('app.forms.customers_save', { amount: '$X.XX' }) }}`
- **Sale badge**: `{{ t('app.forms.sale_badge') }}`
- **Variant discount label**: `{{ t('app.forms.variant.discount_price') }}`

### 2. MenuList.vue
- **Sale badges**: `{{ t('app.forms.sale_badge') }}`
- Applied to all discount price displays in the table

### 3. MenuItemCard.vue
- **Save badge**: `{{ $t('app.forms.save_badge', { amount: '$X.XX' }) }}`
- Shows savings amount on menu item cards

### 4. NewOrderModal.vue
- **Sale badge**: `{{ $t('app.forms.sale_badge') }}`
- Applied to discounted items in order creation

## Usage Examples

### English Display
- Label: "Discount Price (Optional)"
- Help: "When set, this price will be used instead of the regular price"
- Badge: "Sale"
- Savings: "Save $1.50"
- Active: "Discount Active"
- Customer message: "Customers save: $1.50"

### Spanish Display
- Label: "Precio de Descuento (Opcional)"
- Help: "Cuando se establece, este precio se usará en lugar del precio regular"
- Badge: "Oferta"
- Savings: "Ahorra $1.50"
- Active: "Descuento Activo"
- Customer message: "Los clientes ahorran: $1.50"

## Dynamic Values

The translations support dynamic value interpolation using the `{amount}` placeholder:

```javascript
// English
t('app.forms.customers_save', { amount: '$1.50' })
// Output: "Customers save: $1.50"

// Spanish
t('app.forms.customers_save', { amount: '$1.50' })
// Output: "Los clientes ahorran: $1.50"
```

## Testing

To test the translations:

1. **Switch language** in the application settings
2. **Create/edit a menu item** and add a discount price
3. **Verify all labels** appear in the selected language
4. **Check badges** on menu list, cards, and order modal
5. **Confirm savings calculations** display correctly

## Notes

- All hardcoded English text has been replaced with i18n keys
- The translation keys follow the project convention: `app.forms.*`
- Dynamic values (prices, amounts) are passed as parameters
- Dark mode styling is preserved across all translations
