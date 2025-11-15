# Backend Refactoring Plan - Aplicación de SOLID

## Análisis de Archivos Grandes y Violaciones SOLID

### 1. **cash_register.py (664 líneas)** - CRÍTICO ⚠️

**Violaciones SOLID:**
- ❌ **SRP**: Mezcla lógica de sesiones, transacciones, reportes y cálculos
- ❌ **OCP**: Funciones monolíticas difíciles de extender
- ❌ **ISP**: Funciones con muchos parámetros opcionales

**Refactorización Propuesta:**

```
backend/app/services/cash_register/
├── __init__.py
├── session_service.py      # Gestión de sesiones (150 líneas)
├── transaction_service.py  # Gestión de transacciones (120 líneas)
├── report_service.py       # Generación de reportes (200 líneas)
├── calculation_service.py  # Cálculos y agregaciones (100 líneas)
└── denomination_service.py # Conteo de denominaciones (80 líneas)
```

**Beneficios:**
- ✅ Cada módulo tiene una responsabilidad única
- ✅ Fácil testear cada servicio por separado
- ✅ Reducción de 664 líneas a ~5 archivos de 80-200 líneas
- ✅ Mejor organización y mantenibilidad

---

### 2. **subscription_service.py (619 líneas)** - ALTO ⚠️

**Violaciones SOLID:**
- ❌ **SRP**: Mezcla gestión de planes, addons, suscripciones, límites y cálculos
- ❌ **DIP**: Acoplamiento directo a modelos de BD
- ❌ **ISP**: Clase con demasiados métodos (20+)

**Refactorización Propuesta:**

```
backend/app/services/subscription/
├── __init__.py
├── plan_service.py         # Gestión de planes (100 líneas)
├── addon_service.py        # Gestión de addons (100 líneas)
├── subscription_service.py # CRUD de suscripciones (150 líneas)
├── limit_validator.py      # Validación de límites (120 líneas)
├── cost_calculator.py      # Cálculo de costos (80 líneas)
└── discount_service.py     # Aplicación de descuentos (70 líneas)
```

**Beneficios:**
- ✅ Separación clara de responsabilidades
- ✅ Cada servicio es independiente y testeable
- ✅ Fácil agregar nuevos tipos de descuentos o addons
- ✅ Reducción de complejidad cognitiva

---

### 3. **orders.py (647 líneas)** - ALTO ⚠️

**Violaciones SOLID:**
- ❌ **SRP**: Mezcla validaciones, lógica de negocio, gestión de mesas, pagos
- ❌ **OCP**: Lógica de pago hardcodeada en múltiples lugares
- ❌ **DIP**: Acoplamiento directo a servicios de cash_register

**Refactorización Propuesta:**

```
backend/app/api/routers/orders/
├── __init__.py
├── order_routes.py         # Endpoints CRUD básicos (150 líneas)
├── order_item_routes.py    # Endpoints de items (150 líneas)
├── order_extra_routes.py   # Endpoints de extras (120 líneas)
├── order_payment_routes.py # Endpoints de pagos (100 líneas)
└── validators.py           # Validaciones centralizadas (80 líneas)
```

**Servicios adicionales:**

```
backend/app/services/order/
├── __init__.py
├── order_service.py        # CRUD básico (200 líneas)
├── order_item_service.py   # Gestión de items (150 líneas)
├── payment_service.py      # Lógica de pagos (100 líneas)
└── table_manager.py        # Gestión de mesas (80 líneas)
```

**Beneficios:**
- ✅ Endpoints más pequeños y enfocados
- ✅ Lógica de negocio separada de endpoints
- ✅ Fácil agregar nuevos métodos de pago
- ✅ Mejor testabilidad

---

### 4. **order.py service (562 líneas)** - MEDIO ⚠️

**Violaciones SOLID:**
- ❌ **SRP**: Mezcla serialización, CRUD, validaciones y lógica de negocio
- ❌ **OCP**: Función `create_order_with_items` de 180 líneas

**Refactorización Propuesta:**

```
backend/app/services/order/
├── __init__.py
├── order_crud.py           # Operaciones CRUD (150 líneas)
├── order_builder.py        # Construcción de órdenes (120 líneas)
├── order_serializer.py     # Serialización (80 líneas)
├── order_validator.py      # Validaciones (80 líneas)
└── table_availability.py   # Gestión de disponibilidad (80 líneas)
```

**Beneficios:**
- ✅ Función `create_order_with_items` dividida en builder pattern
- ✅ Serialización separada y reutilizable
- ✅ Validaciones centralizadas
- ✅ Cada módulo < 150 líneas

---

### 5. **menu.py router (437 líneas)** - MEDIO ⚠️

**Violaciones SOLID:**
- ❌ **SRP**: Mezcla items, variants y special notes en un solo archivo
- ❌ **ISP**: Función `check_admin` duplicada (líneas 279, 326, 357, 431)

**Refactorización Propuesta:**

```
backend/app/api/routers/menu/
├── __init__.py
├── item_routes.py          # Endpoints de items (200 líneas)
├── variant_routes.py       # Endpoints de variants (150 líneas)
└── special_notes_routes.py # Endpoints de notas (100 líneas)
```

**Mejoras adicionales:**
- Eliminar función `check_admin` duplicada
- Usar `require_admin_or_sysadmin` dependency en todos lados
- Centralizar manejo de errores

**Beneficios:**
- ✅ Endpoints organizados por dominio
- ✅ Eliminación de código duplicado
- ✅ Mejor navegación del código

---

### 6. **cash_register.py router (443 líneas)** - MEDIO ⚠️

**Violaciones SOLID:**
- ❌ **SRP**: Mezcla sesiones, transacciones, reportes y gastos
- ❌ **DRY**: Validación de seguridad duplicada en múltiples endpoints

**Refactorización Propuesta:**

```
backend/app/api/routers/cash_register/
├── __init__.py
├── session_routes.py       # Endpoints de sesiones (150 líneas)
├── transaction_routes.py   # Endpoints de transacciones (100 líneas)
├── report_routes.py        # Endpoints de reportes (150 líneas)
└── dependencies.py         # Validaciones compartidas (50 líneas)
```

**Dependency centralizado:**

```python
# dependencies.py
async def verify_session_access(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> CashRegisterSessionModel:
    """Verifica que el usuario tenga acceso a la sesión."""
    session = cash_register_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user.restaurant_id and session.restaurant_id != current_user.restaurant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "staff" and current_user.staff_type == "cashier":
        if session.cashier_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permiso")
    
    return session
```

**Beneficios:**
- ✅ Validación de seguridad centralizada (DRY)
- ✅ Endpoints más limpios y enfocados
- ✅ Fácil agregar nuevos tipos de reportes

---

## Archivos Pequeños que Necesitan Mejoras

### 7. **base.py (111 líneas)** - BAJO ⚠️

**Problema:**
- Clase `BaseRouter` y `CRUDRouter` no se usan en el proyecto
- Código muerto que debe eliminarse

**Acción:**
- ❌ Eliminar archivo completo si no se usa
- O documentar su propósito si es para uso futuro

---

## Patrones de Diseño Recomendados

### 1. **Repository Pattern** (para servicios)

```python
# backend/app/repositories/order_repository.py
class OrderRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, order_id: int) -> Optional[OrderModel]:
        return self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    def get_all(self, restaurant_id: int, filters: dict) -> List[OrderModel]:
        query = self.db.query(OrderModel).filter(OrderModel.restaurant_id == restaurant_id)
        # Apply filters...
        return query.all()
```

**Beneficios:**
- ✅ Separación de lógica de acceso a datos
- ✅ Fácil mockear en tests
- ✅ DIP: Servicios dependen de abstracción, no de SQLAlchemy

---

### 2. **Builder Pattern** (para órdenes complejas)

```python
# backend/app/services/order/order_builder.py
class OrderBuilder:
    def __init__(self, db: Session, restaurant_id: int):
        self.db = db
        self.restaurant_id = restaurant_id
        self.order = None
        self.items = []
        self.persons = []
    
    def create_base_order(self, order_data: OrderCreate) -> 'OrderBuilder':
        # Crear orden base
        return self
    
    def add_items(self, items: List[OrderItemCreate]) -> 'OrderBuilder':
        # Agregar items
        return self
    
    def add_persons(self, persons: List[PersonCreate]) -> 'OrderBuilder':
        # Agregar personas
        return self
    
    def calculate_total(self) -> 'OrderBuilder':
        # Calcular total
        return self
    
    def build(self) -> OrderModel:
        # Construir y retornar orden completa
        return self.order
```

**Uso:**

```python
order = (OrderBuilder(db, restaurant_id)
    .create_base_order(order_data)
    .add_items(order_data.items)
    .add_persons(order_data.persons)
    .calculate_total()
    .build())
```

**Beneficios:**
- ✅ Código más legible
- ✅ Fácil agregar nuevos pasos
- ✅ OCP: Extendible sin modificar código existente

---

### 3. **Strategy Pattern** (para cálculos de reportes)

```python
# backend/app/services/cash_register/report_strategies.py
from abc import ABC, abstractmethod

class ReportStrategy(ABC):
    @abstractmethod
    def generate(self, session: CashRegisterSessionModel) -> dict:
        pass

class DailySummaryStrategy(ReportStrategy):
    def generate(self, session: CashRegisterSessionModel) -> dict:
        # Lógica específica para daily summary
        pass

class WeeklySummaryStrategy(ReportStrategy):
    def generate(self, sessions: List[CashRegisterSessionModel]) -> dict:
        # Lógica específica para weekly summary
        pass

class CashDifferenceStrategy(ReportStrategy):
    def generate(self, session: CashRegisterSessionModel) -> dict:
        # Lógica específica para cash difference
        pass
```

**Beneficios:**
- ✅ Fácil agregar nuevos tipos de reportes
- ✅ OCP: Cerrado para modificación, abierto para extensión
- ✅ Cada estrategia es testeable independientemente

---

## Plan de Implementación

### Fase 1: Servicios Críticos (Semana 1)
1. ✅ Refactorizar `cash_register.py` service → 5 módulos
2. ✅ Refactorizar `subscription_service.py` → 6 módulos
3. ✅ Crear tests unitarios para cada módulo nuevo

### Fase 2: Routers (Semana 2)
1. ✅ Refactorizar `orders.py` router → 5 archivos
2. ✅ Refactorizar `menu.py` router → 3 archivos
3. ✅ Refactorizar `cash_register.py` router → 4 archivos
4. ✅ Centralizar validaciones de seguridad

### Fase 3: Servicios de Orden (Semana 3)
1. ✅ Refactorizar `order.py` service → 5 módulos
2. ✅ Implementar Builder Pattern para órdenes
3. ✅ Implementar Repository Pattern
4. ✅ Crear tests de integración

### Fase 4: Limpieza y Optimización (Semana 4)
1. ✅ Eliminar código muerto (`base.py`)
2. ✅ Eliminar duplicación de código
3. ✅ Documentar nuevos módulos con docstrings
4. ✅ Code review completo

---

## Métricas de Éxito

**Antes:**
- 6 archivos > 400 líneas
- Funciones > 100 líneas
- Alta complejidad ciclomática
- Difícil testear

**Después:**
- ✅ Todos los archivos < 200 líneas
- ✅ Funciones < 50 líneas
- ✅ Complejidad ciclomática < 10
- ✅ Cobertura de tests > 80%
- ✅ Separación clara de responsabilidades
- ✅ Código extensible y mantenible

---

## Checklist de Refactorización

Para cada módulo refactorizado:
- [ ] **SRP**: ¿Tiene una sola responsabilidad?
- [ ] **OCP**: ¿Es fácil extender sin modificar?
- [ ] **LSP**: ¿Los tipos son intercambiables?
- [ ] **ISP**: ¿Las interfaces son pequeñas y específicas?
- [ ] **DIP**: ¿Depende de abstracciones?
- [ ] **Tests**: ¿Tiene tests unitarios?
- [ ] **Docs**: ¿Tiene docstrings claros?
- [ ] **Líneas**: ¿Menos de 200 líneas?

---

## Notas Importantes

1. **No romper funcionalidad existente**: Refactorizar con tests
2. **Migración gradual**: Un módulo a la vez
3. **Mantener compatibilidad**: Usar deprecation warnings si es necesario
4. **Documentar cambios**: Actualizar README y docs
5. **Code review**: Cada refactorización debe ser revisada

---

## Prioridad de Ejecución

1. 🔴 **CRÍTICO**: `cash_register.py` service (664 líneas)
2. 🔴 **CRÍTICO**: `subscription_service.py` (619 líneas)
3. 🟠 **ALTO**: `orders.py` router (647 líneas)
4. 🟠 **ALTO**: `order.py` service (562 líneas)
5. 🟡 **MEDIO**: `menu.py` router (437 líneas)
6. 🟡 **MEDIO**: `cash_register.py` router (443 líneas)
7. 🟢 **BAJO**: Eliminar `base.py` (código muerto)
