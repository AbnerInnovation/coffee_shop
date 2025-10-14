# Discount Price Feature

## Overview
This feature allows you to set promotional/discount prices on menu items and variants. When a discount price is set and is greater than zero, it automatically replaces the original price throughout the system, including in orders.

## Backend Changes

### 1. Database Models (`backend/app/models/menu.py`)
Added `discount_price` field to both `MenuItem` and `MenuItemVariant` models:
- **Type**: `Optional[float]`
- **Default**: `None`
- **Behavior**: When set and > 0, this price is used instead of the regular price

Added helper methods:
- `MenuItem.get_effective_price()` - Returns discount_price if set and > 0, otherwise returns regular price
- `MenuItemVariant.get_effective_price()` - Same logic for variants

### 2. Database Migration (`backend/migrations/versions/add_discount_price_to_menu.py`)
- Adds `discount_price` column to `menu_items` table
- Adds `discount_price` column to `menu_item_variants` table
- **Important**: Update the `down_revision` to point to your latest migration before running

### 3. API Schemas (`backend/app/schemas/menu.py`)
Updated all menu schemas to include `discount_price`:
- `MenuItemBase`
- `MenuItemUpdate`
- `MenuItemVariantBase`
- `MenuItemVariantUpdate`

### 4. Order Service (`backend/app/services/order.py`)
Updated to use `get_effective_price()` method when:
- Creating new orders
- Adding items to existing orders
- Updating order items

This ensures that discount prices are automatically applied to all orders.

## Frontend Changes

### 1. TypeScript Types (`frontend/src/types/menu.ts`)
Updated interfaces to include `discount_price`:
- `MenuItem`
- `MenuItemVariant`
- `MenuItemFormData`

### 2. Menu Service (`frontend/src/services/menuService.ts`)
- Updated `MenuItemResponse` interface
- Updated `normalizeMenuItem()` to handle discount_price
- Updated create/update payloads to include discount_price

## How It Works

### Setting a Discount Price
1. Edit a menu item or variant
2. Set the `discount_price` field to your promotional price
3. Save the changes

### Automatic Price Replacement
- If `discount_price` is `null` or `0`: Regular price is used
- If `discount_price` > `0`: Discount price replaces the regular price everywhere

### Where Discount Prices Apply
- ✅ Order creation
- ✅ Adding items to orders
- ✅ Order item updates
- ✅ Total calculations
- ✅ Cash register transactions (via order totals)

## Usage Examples

### Example 1: Seasonal Promotion
```python
# Regular price: $5.00
# Discount price: $3.99
# Customer pays: $3.99
```

### Example 2: No Discount
```python
# Regular price: $5.00
# Discount price: None (or 0)
# Customer pays: $5.00
```

### Example 3: Variant-Specific Discount
```python
# Coffee - Regular price: $4.00
# Coffee - Large variant:
#   - Regular price: $5.00
#   - Discount price: $4.50
#   - Customer pays: $4.50 for large
```

## Migration Steps ✅ COMPLETED

The database migration has been successfully applied!

1. **Database migration** ✅
   ```bash
   cd backend
   alembic upgrade head
   ```
   Status: The `discount_price` columns have been added to both `menu_items` and `menu_item_variants` tables.

2. **Restart the backend server**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Frontend will automatically pick up the changes** (no rebuild needed if using dev server)

## UI Updates Completed ✅

All frontend UI components have been updated to support discount pricing with full i18n support (English & Spanish):

### Menu Management UI ✅
1. **Menu Item Form** (`MenuItemForm.vue`)
   - Added discount price input field for menu items
   - Added discount price input field in variant modal
   - Shows real-time savings calculation when discount is set
   - Visual indicator (green badge) shows "Discount Active" with savings amount

2. **Variant Display**
   - Variants list shows both regular and discount prices
   - Strikethrough on original price when discount is active
   - Green "Sale" badge for discounted variants
   - Discount price displayed in green color

### Menu Display UI ✅
1. **Menu Item Card** (`MenuItemCard.vue`)
   - Shows original price with strikethrough when discounted
   - Displays discount price in bold green
   - Shows savings amount in a green badge ("Save $X.XX")
   - Clean, professional layout with dark mode support

### Order UI ✅
1. **New Order Modal** (`NewOrderModal.vue`)
   - Menu items show discount prices with visual indicators
   - Original price shown with strikethrough
   - Discount price highlighted in green
   - "Sale" badge for promotional items
   - Automatic price calculation uses discount prices
   - Helper functions ensure correct pricing throughout order flow

### UI Pattern Implemented
```
Regular Price: $5.00  ← Strikethrough (gray)
Discount Price: $3.99 ← Bold green
[Sale] or [Save $1.01] ← Green badge
```

### Internationalization (i18n) ✅
Full bilingual support with professional translations:
- **English**: "Discount Price", "Sale", "Save $X.XX", "Customers save"
- **Spanish**: "Precio de Descuento", "Oferta", "Ahorra $X.XX", "Los clientes ahorran"
- All UI elements automatically switch based on user's language preference
- See `I18N_DISCOUNT_TRANSLATIONS.md` for complete translation reference

## API Endpoints

All existing menu endpoints now support discount_price:

- `GET /api/menu` - Returns items with discount_price
- `POST /api/menu` - Create item with optional discount_price
- `PUT /api/menu/{id}` - Update item including discount_price
- `POST /api/menu/{id}/variants` - Create variant with optional discount_price
- `PUT /api/menu/{id}/variants/{variant_id}` - Update variant discount_price

## Testing Checklist

- [ ] Create menu item with discount price
- [ ] Create menu item without discount price
- [ ] Update existing item to add discount price
- [ ] Update existing item to remove discount price (set to null/0)
- [ ] Create order with discounted item - verify correct price used
- [ ] Create order with non-discounted item - verify regular price used
- [ ] Add discounted item to existing order
- [ ] Verify cash register transactions use correct prices
- [ ] Test variant-specific discounts
- [ ] Test mixed orders (some items discounted, some not)

## Notes

- Discount prices are stored separately from regular prices
- Regular prices are never modified when setting discounts
- You can easily remove a discount by setting discount_price to null or 0
- The system automatically chooses the effective price at order time
- Historical orders maintain their original prices (stored in order_items.unit_price)
