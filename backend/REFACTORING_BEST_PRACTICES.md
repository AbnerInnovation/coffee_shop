# Refactoring Best Practices

## 🎯 Objetivo

Este documento establece las mejores prácticas para realizar refactorizaciones seguras y efectivas en el backend, evitando errores como el bug de conteo de usuarios (role vs staff_type).

---

## ✅ Pre-Refactorización Checklist

### 1. Entender el Código Actual

- [ ] Leer y comprender completamente el código a refactorizar
- [ ] Identificar todas las dependencias y usos
- [ ] Documentar asunciones y casos edge
- [ ] Revisar el modelo de datos (estructura de tablas, relaciones)
- [ ] Identificar soft deletes, multi-tenancy, y otras consideraciones

**Ejemplo de asunciones críticas:**
```python
# IMPORTANTE: Documentar estructura de usuarios
# - Admin: role='admin' (sin staff_type)
# - Staff: role='staff' + staff_type in ['waiter', 'cashier', 'kitchen']
# - Owner: role='owner' (sin staff_type)
# - Soft delete: deleted_at IS NULL para usuarios activos
```

### 2. Crear Tests ANTES de Refactorizar

- [ ] Crear tests unitarios para funcionalidad actual
- [ ] Crear tests de integración para endpoints
- [ ] Verificar que todos los tests pasen
- [ ] Documentar casos edge en tests

**Ejemplo:**
```python
def test_counts_staff_by_type_not_role():
    """
    CRITICAL: Staff users must be counted by staff_type, not role.
    Bug history: Initially counted by role='waiter' which was wrong.
    """
    # Test implementation...
```

### 3. Planificar la Refactorización

- [ ] Definir estructura de módulos
- [ ] Identificar responsabilidades (SRP)
- [ ] Planificar migración gradual si es posible
- [ ] Considerar backward compatibility

---

## 🔨 Durante la Refactorización

### 1. Mantener la Lógica de Negocio

```python
# ❌ MAL: Asumir estructura
def get_users(db, role):
    return db.query(User).filter(User.role == role).all()

# ✅ BIEN: Considerar estructura real
def get_users(db, role, staff_type=None):
    """
    Get users by role and optional staff_type.
    
    IMPORTANT: Staff users have role='staff' and staff_type.
    Admin/Owner users have role='admin'/'owner' without staff_type.
    """
    query = db.query(User).filter(User.role == role)
    if staff_type and role == 'staff':
        query = query.filter(User.staff_type == staff_type)
    return query.all()
```

### 2. Agregar Logging

```python
import logging
logger = logging.getLogger(__name__)

def get_current_usage(db: Session, restaurant_id: int):
    logger.debug(f"Calculating usage for restaurant {restaurant_id}")
    
    waiter_count = db.query(User).filter(
        User.restaurant_id == restaurant_id,
        User.role == 'staff',
        User.staff_type == 'waiter',
        User.deleted_at.is_(None)
    ).count()
    
    logger.debug(f"Found {waiter_count} waiters")
    return {'users_waiter': waiter_count}
```

### 3. Validar Queries SQL

```python
# Imprimir query SQL para verificar
from sqlalchemy import inspect

query = db.query(User).filter(User.role == 'staff')
print(str(query))  # Ver SQL generado

# Usar EXPLAIN para queries complejos
```

### 4. Comparación Paralela (Opcional)

```python
def get_usage_with_validation(db, restaurant_id):
    """Run both implementations and compare"""
    new_result = get_current_usage_new(db, restaurant_id)
    old_result = get_current_usage_old(db, restaurant_id)
    
    if new_result != old_result:
        logger.error(f"MISMATCH: new={new_result}, old={old_result}")
        # Alert or use old result temporarily
    
    return new_result
```

---

## ✅ Post-Refactorización Checklist

### 1. Ejecutar Tests

- [ ] Ejecutar todos los tests unitarios
- [ ] Ejecutar tests de integración
- [ ] Verificar cobertura de código
- [ ] Revisar logs de errores

```bash
# Ejecutar tests
pytest tests/services/subscription/ -v

# Con cobertura
pytest --cov=app/services/subscription tests/services/subscription/

# Solo tests relacionados
pytest -k "limit_validator" -v
```

### 2. Verificación Manual

- [ ] Probar en UI todas las funcionalidades afectadas
- [ ] Verificar con datos reales (staging)
- [ ] Revisar logs de aplicación
- [ ] Verificar performance (no degradación)

**Checklist UI para Subscription Usage:**
- [ ] Contador de administradores correcto
- [ ] Contador de meseros correcto
- [ ] Contador de cajeros correcto
- [ ] Contador de cocina correcto
- [ ] Porcentajes calculados correctamente
- [ ] Límites mostrados correctamente
- [ ] Usuarios eliminados no cuentan

### 3. Code Review

- [ ] Solicitar code review de otro desarrollador
- [ ] Verificar que se mantiene lógica de negocio
- [ ] Revisar manejo de casos edge
- [ ] Verificar documentación y comentarios

---

## 📋 Checklist Específico por Tipo

### Refactorización de Servicios

- [ ] Separar responsabilidades (SRP)
- [ ] Mantener mismas firmas de función (o deprecar gradualmente)
- [ ] Agregar type hints
- [ ] Documentar con docstrings
- [ ] Crear tests unitarios para cada función
- [ ] Validar que queries SQL son eficientes

### Refactorización de Routers/Endpoints

- [ ] Mantener mismos endpoints (backward compatibility)
- [ ] Mantener misma estructura de respuesta
- [ ] Validar autenticación y autorización
- [ ] Verificar manejo de errores
- [ ] Probar con Postman/Thunder Client
- [ ] Actualizar documentación de API

### Refactorización de Modelos

- [ ] Crear migración de base de datos
- [ ] Verificar relaciones (foreign keys)
- [ ] Mantener soft deletes
- [ ] Verificar índices
- [ ] Probar rollback de migración
- [ ] Actualizar fixtures de tests

---

## 🐛 Lecciones Aprendidas

### Bug: Conteo Incorrecto de Usuarios (Nov 2024)

**Problema:**
```python
# ❌ Código incorrecto
for role in ['admin', 'waiter', 'cashier', 'kitchen']:
    count = db.query(User).filter(User.role == role).count()
```

**Causa:**
- No se consideró que staff users tienen `role='staff'` + `staff_type`
- Se asumió que `role` diferenciaba todos los tipos

**Solución:**
```python
# ✅ Código correcto
if role == 'admin':
    count = db.query(User).filter(User.role == 'admin').count()
elif role in ['waiter', 'cashier', 'kitchen']:
    count = db.query(User).filter(
        User.role == 'staff',
        User.staff_type == role
    ).count()
```

**Prevención:**
- Tests que verifican estructura role/staff_type
- Documentación de modelo de datos
- Code review enfocado en queries

---

## 🔧 Herramientas Útiles

### 1. Tests Automatizados

```bash
# Ejecutar tests antes de refactorizar
pytest tests/ -v

# Ejecutar tests después de refactorizar
pytest tests/ -v --cov=app/services

# Tests de regresión
pytest tests/ -v --lf  # Solo tests que fallaron
```

### 2. Logging

```python
# Configurar logging detallado durante refactorización
import logging
logging.basicConfig(level=logging.DEBUG)

# En producción, usar nivel INFO
logging.basicConfig(level=logging.INFO)
```

### 3. Feature Flags

```python
# Para migración gradual
USE_NEW_IMPLEMENTATION = os.getenv('USE_NEW_IMPL', 'false') == 'true'

if USE_NEW_IMPLEMENTATION:
    result = new_function()
else:
    result = old_function()
```

### 4. Monitoring

```python
# Agregar métricas para comparar
import time

start = time.time()
result = new_function()
duration = time.time() - start

logger.info(f"new_function took {duration:.2f}s")
```

---

## 📚 Recursos

- **SOLID Principles**: https://en.wikipedia.org/wiki/SOLID
- **Refactoring Patterns**: https://refactoring.guru/
- **Testing Best Practices**: https://docs.pytest.org/
- **SQLAlchemy Query Guide**: https://docs.sqlalchemy.org/

---

## 🎯 Regla de Oro

> **"Si no tienes tests, no refactorices. Si refactorizas, crea tests."**

Cada refactorización debe:
1. Mantener funcionalidad existente
2. Mejorar estructura del código
3. Estar cubierta por tests
4. Ser verificada manualmente

---

**Última actualización:** Noviembre 2024  
**Mantenido por:** Equipo de Desarrollo
