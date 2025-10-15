# Running Database Migrations

## Fixed Migration Issue

The "multiple heads" error has been resolved. The performance indexes migration now correctly follows the existing migration chain.

## Migration Chain (Current)

```
feaf3a486270 (initial_migration)
    ↓
01e6bf410b36 (add_cash_register)
    ↓
e2fc30e12ba0 (add_payment_method_to_orders)
    ↓
[branches merged at 9ec8b365ef74]
    ↓
a1b2c3d4e5f6 (make_datetimes_timezone_aware)
    ↓
add_expense_type (add_expense_transaction_type)
    ↓
add_payment_method_tx (add_payment_method_to_transactions)
    ↓
add_discount_price_menu (add_discount_price_to_menu)
    ↓
f1a2b3c4d5e6 (add_performance_indexes) ← NEW
```

## Run the Migration

```bash
cd backend
source venv/Scripts/activate  # Already activated
alembic upgrade head
```

## Expected Output

```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade add_discount_price_menu -> f1a2b3c4d5e6, add_performance_indexes
```

## Verify Indexes Were Created

After running the migration, verify the indexes:

```sql
-- Connect to MySQL
mysql -u root -p coffee_shop

-- Check indexes on orders table
SHOW INDEX FROM orders;

-- Check indexes on menu_items table
SHOW INDEX FROM menu_items;

-- Check indexes on users table
SHOW INDEX FROM users;
```

## If You Still Get Errors

If you still see "multiple heads" error, check current state:

```bash
# Check which migrations are applied
alembic current

# Check all available heads
alembic heads

# Show full history
alembic history
```

## Rollback (If Needed)

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade add_discount_price_menu
```

## Troubleshooting

### Error: "Can't locate revision identified by 'add_discount_price_menu'"

This means the migration hasn't been applied yet. Run:

```bash
alembic upgrade add_discount_price_menu
alembic upgrade head
```

### Error: "Target database is not up to date"

Check current version:

```bash
alembic current
```

Then upgrade step by step if needed.
