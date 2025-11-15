# Orders Router Refactoring Plan - Fase 3

## 📊 Análisis Inicial

**Archivo:** `app/api/routers/orders.py`  
**Líneas:** 646  
**Endpoints:** 14  
**Complejidad:** Alta - Mucha lógica de negocio en el router

---

## 🔍 Problemas Identificados

### 1. **Violación de SRP (Single Responsibility Principle)**
El router mezcla:
- Validación de datos
- Lógica de negocio (cambio de estado de mesas, pagos)
- Manejo de transacciones de caja
- Actualización de múltiples modelos
- Control de acceso (waiters vs admins)

### 2. **Código Duplicado**
- Validación de `MenuItem` repetida en múltiples endpoints
- Validación de `Table` repetida
- Lógica de "marcar mesa disponible" duplicada
- Validación de permisos repetida

### 3. **Endpoints Complejos**

#### `update_order` (líneas 117-214) - 98 líneas
- Maneja cambio de tipo de orden (dine-in ↔ takeaway/delivery)
- Maneja cambio de mesa
- Maneja pago de orden
- Crea transacción de caja
- Actualiza estado de mesa
- **Demasiadas responsabilidades**

#### `mark_order_as_paid` (líneas 376-458) - 83 líneas
- Validación compleja de estado
- Creación de transacción de caja
- Actualización de mesa
- Manejo de errores específicos
- **Lógica de negocio compleja**

### 4. **Dependencias Mezcladas**
```python
from ...services import order as order_service
from ...services.order import serialize_order_item, mark_table_available_if_no_orders
from ...services.cash_register import create_transaction_from_order
```
- Mezcla imports de módulo y funciones específicas
- No está claro qué viene de dónde

---

## 🎯 Estrategia de Refactorización

### Principio: **NO TOCAR EL ROUTER**

A diferencia de las fases anteriores, **NO vamos a refactorizar el router** porque:
1. ✅ Ya usa `order_service` para la mayoría de operaciones
2. ✅ El router es solo una capa de presentación/validación
3. ⚠️ La complejidad está en la **lógica de negocio mezclada**

### Enfoque: **Extraer Lógica de Negocio**

Vamos a:
1. Identificar lógica de negocio en el router
2. Moverla a servicios especializados
3. Mantener el router delgado (solo validación y orquestación)

---

## 📁 Estructura Propuesta

```
app/services/orders/
├── __init__.py              # Exports centralizados
├── order_crud.py            # CRUD básico de órdenes
├── order_items_crud.py      # CRUD de items de orden
├── order_extras_crud.py     # CRUD de extras de items
├── payment_service.py       # Lógica de pagos
├── table_manager.py         # Gestión de mesas (ocupación)
└── validators.py            # Validaciones reutilizables
```

---

## 🔧 Módulos Detallados

### 1. `order_crud.py`
**Responsabilidad:** CRUD básico de órdenes

```python
def get_orders(db, restaurant_id, skip, limit, sort_by, status, table_id, waiter_id, hours)
def get_order(db, order_id, restaurant_id)
def create_order_with_items(db, order, restaurant_id, user_id)
def update_order(db, db_order, order)
def delete_order(db, order_id, restaurant_id)
```

### 2. `order_items_crud.py`
**Responsabilidad:** Gestión de items de orden

```python
def add_order_item(db, order_id, item, restaurant_id)
def add_multiple_items(db, order_id, items, restaurant_id)
def update_order_item(db, order_id, item_id, item, restaurant_id)
def update_order_item_status(db, order_id, item_id, status, restaurant_id)
def delete_order_item(db, order_id, item_id, restaurant_id)
```

### 3. `order_extras_crud.py`
**Responsabilidad:** Gestión de extras de items

```python
def add_extra_to_item(db, order_id, item_id, extra, restaurant_id)
def get_item_extras(db, order_id, item_id, restaurant_id)
def update_item_extra(db, order_id, item_id, extra_id, extra, restaurant_id)
def delete_item_extra(db, order_id, item_id, extra_id, restaurant_id)
```

### 4. `payment_service.py` ⭐ **NUEVO**
**Responsabilidad:** Lógica de pagos y transacciones

```python
def process_order_payment(db, order_id, payment_method, user_id, restaurant_id)
    """
    Procesa el pago de una orden:
    1. Valida que la orden no esté pagada
    2. Marca orden como pagada
    3. Actualiza estado a COMPLETED
    4. Libera mesa si es dine-in
    5. Crea transacción en caja registradora
    """

def validate_payment_method(payment_method)
def can_cancel_order(order, user_role)
```

### 5. `table_manager.py` ⭐ **NUEVO**
**Responsabilidad:** Gestión de ocupación de mesas

```python
def mark_table_occupied(db, table_id)
def mark_table_available_if_no_orders(db, table_id, exclude_order_id)
def handle_table_change(db, old_table_id, new_table_id, order_type, order_id)
    """
    Maneja cambios de mesa en una orden:
    - dine-in → takeaway: libera mesa
    - takeaway → dine-in: ocupa mesa
    - cambio de mesa: libera antigua, ocupa nueva
    """
```

### 6. `validators.py` ⭐ **NUEVO**
**Responsabilidad:** Validaciones reutilizables

```python
def validate_menu_item_exists(db, item_id)
def validate_table_exists(db, table_id)
def validate_order_exists(db, order_id, restaurant_id)
def validate_order_item_exists(db, order_id, item_id, restaurant_id)
def validate_can_modify_order(order, user)
```

---

## 🚀 Plan de Implementación

### Paso 1: Crear Estructura Base ✅
- [x] Crear directorio `app/services/orders/`
- [x] Crear `__init__.py` con exports

### Paso 2: Extraer Lógica Existente
- [ ] Mover funciones de `order_service.py` a módulos especializados
- [ ] Mantener `order_service.py` como wrapper de compatibilidad

### Paso 3: Crear Nuevos Servicios
- [ ] Implementar `payment_service.py`
- [ ] Implementar `table_manager.py`
- [ ] Implementar `validators.py`

### Paso 4: Refactorizar Router
- [ ] Extraer lógica de `update_order` a servicios
- [ ] Extraer lógica de `mark_order_as_paid` a `payment_service`
- [ ] Usar validadores en lugar de código duplicado

### Paso 5: Tests
- [ ] Crear tests para `payment_service.py`
- [ ] Crear tests para `table_manager.py`
- [ ] Crear tests para `validators.py`
- [ ] Verificar que todos los tests existentes pasen

---

## ⚠️ Consideraciones Críticas

### 1. **Transacciones de Base de Datos**
```python
# ANTES (en router)
db_order.is_paid = True
db.commit()
create_transaction_from_order(db, order_id, user_id)

# DESPUÉS (en payment_service)
def process_order_payment(db, order_id, payment_method, user_id):
    # Todo en una transacción
    try:
        order = mark_order_as_paid(db, order_id, payment_method)
        create_cash_transaction(db, order, user_id)
        release_table_if_needed(db, order)
        db.commit()
        return order
    except Exception as e:
        db.rollback()
        raise
```

### 2. **Manejo de Mesas**
```python
# Casos a considerar:
# 1. dine-in → takeaway: liberar mesa
# 2. takeaway → dine-in: ocupar mesa
# 3. cambio de mesa: liberar antigua, ocupar nueva
# 4. orden cancelada: liberar mesa
# 5. orden pagada: liberar mesa si no hay otras órdenes
```

### 3. **Permisos y Roles**
```python
# Waiters: solo ven sus órdenes
# Admin/Sysadmin: pueden cancelar órdenes
# Todos: pueden crear órdenes
```

---

## 📋 Checklist de Seguridad

Antes de cada cambio:
- [ ] Leer y entender el código actual
- [ ] Identificar casos edge (mesas, pagos, cancelaciones)
- [ ] Crear tests para comportamiento actual
- [ ] Documentar asunciones

Durante la refactorización:
- [ ] Mantener misma lógica de negocio
- [ ] No asumir estructura de datos
- [ ] Verificar transacciones de DB
- [ ] Comparar resultados antes/después

Post-refactorización:
- [ ] Ejecutar todos los tests
- [ ] Verificar manualmente en UI
- [ ] Revisar logs de errores
- [ ] Code review

---

## 🎯 Resultado Esperado

### Antes:
```python
# Router con 98 líneas de lógica de negocio
@router.put("/{order_id}")
async def update_order(...):
    # Validación de tabla
    # Cambio de tipo de orden
    # Manejo de mesa
    # Pago de orden
    # Transacción de caja
    # ... 98 líneas
```

### Después:
```python
# Router delgado (solo orquestación)
@router.put("/{order_id}")
async def update_order(...):
    db_order = validators.validate_order_exists(db, order_id, restaurant.id)
    
    if order.is_paid:
        return payment_service.process_order_payment(
            db, order_id, order.payment_method, current_user.id
        )
    
    if order.table_id != db_order.table_id:
        table_manager.handle_table_change(
            db, db_order.table_id, order.table_id, 
            order.order_type, order_id
        )
    
    return order_crud.update_order(db, db_order, order)
```

---

**Última actualización:** Noviembre 2024  
**Estado:** En Progreso - Fase 3
