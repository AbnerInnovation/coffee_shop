# Pendientes - Coffee Shop Admin

## 🔴 Alta Prioridad

### 1. Protección de Endpoints del Backend
**Estado:** ⬜ Pendiente

**Descripción:**
Implementar validación de roles en todos los endpoints del backend para asegurar que la protección no sea solo en el frontend.

**Tareas:**
- [ ] Crear decorator/dependency `require_admin` en FastAPI
- [ ] Crear decorator/dependency `require_role` genérico
- [ ] Proteger endpoints de menú (POST, PUT, DELETE, PATCH)
- [ ] Proteger endpoints de categorías (POST, PUT, DELETE)
- [ ] Proteger endpoints de mesas (POST, PUT, DELETE)
- [ ] Proteger endpoints de usuarios (POST, PUT, DELETE)
- [ ] Proteger endpoints de suscripción (GET, POST, PUT)
- [ ] Proteger endpoints de reportes
- [ ] Agregar tests de permisos en backend

**Archivos a modificar:**
```
backend/app/api/deps.py              # Agregar dependencies de roles
backend/app/api/routers/menu.py      # Proteger endpoints
backend/app/api/routers/categories.py
backend/app/api/routers/tables.py
backend/app/api/routers/users.py
backend/app/api/routers/subscription.py
```

**Ejemplo de implementación:**
```python
# backend/app/api/deps.py
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or sysadmin role"""
    if current_user.role not in ['admin', 'sysadmin']:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user

# Uso en endpoints
@router.post("/items/")
async def create_menu_item(
    item: MenuItemCreate,
    current_user: User = Depends(require_admin)  # ← Protegido
):
    ...
```

---

### 2. Implementación de Sub-roles de Staff
**Estado:** ⬜ Pendiente

**Descripción:**
Implementar sistema de sub-roles para el rol STAFF (waiter, cashier, kitchen, general) con permisos específicos para cada tipo.

**Sub-roles a implementar:**
- **WAITER** (Mesero): Crear/editar pedidos, gestionar mesas
- **CASHIER** (Cajero): Procesar pagos, acceder a caja registradora
- **KITCHEN** (Cocina): Ver pedidos de cocina, marcar items preparados
- **GENERAL** (General): Solo lectura

**Tareas Backend:**
- [ ] Agregar campo `staff_type` a modelo User
- [ ] Crear migración de base de datos
- [ ] Actualizar esquemas Pydantic
- [ ] Modificar endpoint de creación de usuarios
- [ ] Actualizar límites de suscripción por sub-rol

**Tareas Frontend:**
- [ ] Actualizar formulario de usuario con selector de staff_type
- [ ] Actualizar funciones de permisos en `utils/permissions.ts`
- [ ] Actualizar composable `usePermissions.ts`
- [ ] Actualizar rutas con permisos específicos por sub-rol
- [ ] Actualizar navegación según sub-rol
- [ ] Agregar traducciones para sub-roles

**Archivos a modificar:**

**Backend:**
```
backend/app/models/user.py           # Agregar staff_type
backend/app/schemas/user.py          # Agregar staff_type
backend/app/api/routers/users.py     # Validar staff_type
backend/migrations/versions/xxx.py   # Migración
```

**Frontend:**
```
frontend/src/utils/permissions.ts    # Actualizar funciones
frontend/src/composables/usePermissions.ts
frontend/src/components/users/UserFormModal.vue
frontend/src/locales/es.json         # Traducciones
```

**Matriz de permisos por sub-rol:**
```
| Acción              | WAITER | CASHIER | KITCHEN | GENERAL |
|---------------------|--------|---------|---------|---------|
| Crear pedidos       | ✅     | ❌      | ❌      | ❌      |
| Ver pedidos         | ✅     | ✅      | ✅      | ❌      |
| Editar pedidos      | ✅     | ❌      | ❌      | ❌      |
| Gestionar mesas     | ✅     | ❌      | ❌      | ❌      |
| Procesar pagos      | ❌     | ✅      | ❌      | ❌      |
| Acceder a caja      | ❌     | ✅      | ❌      | ❌      |
| Ver cocina          | ❌     | ❌      | ✅      | ❌      |
| Marcar preparados   | ❌     | ❌      | ✅      | ❌      |
| Ver menú            | ✅     | ✅      | ✅      | ✅      |
```

---

## 🟡 Media Prioridad

### 3. Aplicar Permisos a Otras Vistas
**Estado:** ⬜ Pendiente

**Descripción:**
Aplicar el módulo de permisos a las vistas que aún no lo tienen.

**Vistas a actualizar:**
- [ ] CategoriesView.vue - Botones de crear/editar/eliminar
- [ ] TablesView.vue - Botones de crear/editar/eliminar
- [ ] OrdersView.vue - Botones según rol
- [ ] CashRegisterView.vue - Acceso completo
- [ ] KitchenView.vue - Acceso completo
- [ ] DashboardView.vue - Widgets según permisos

**Patrón a seguir (igual que MenuList.vue):**
```vue
<script setup>
import { usePermissions } from '@/composables/usePermissions';

const { canEditCategories } = usePermissions();
</script>

<template>
  <button v-if="canEditCategories">
    Agregar Categoría
  </button>
</template>
```

---

### 4. Actualizar Navegación con Permisos
**Estado:** ⬜ Pendiente

**Descripción:**
Actualizar App.vue para ocultar enlaces de navegación según permisos del usuario.

**Tareas:**
- [ ] Actualizar menú desktop con permisos
- [ ] Actualizar menú móvil con permisos
- [ ] Crear computed property con navegación filtrada
- [ ] Agregar badges de "Admin" en enlaces administrativos

**Archivo a modificar:**
```
frontend/src/App.vue
```

**Ejemplo:**
```vue
<script setup>
import { usePermissions } from '@/composables/usePermissions';

const {
  canManageTables,
  canEditCategories,
  canAccessCashRegister,
  canAccessKitchen,
  canManageUsers,
  canViewSubscription
} = usePermissions();

const navigation = computed(() => [
  { name: 'Menú', to: '/menu', show: true },
  { name: 'Categorías', to: '/categories', show: canEditCategories.value },
  { name: 'Mesas', to: '/tables', show: canManageTables.value },
  { name: 'Pedidos', to: '/orders', show: true },
  { name: 'Cocina', to: '/kitchen', show: canAccessKitchen.value },
  { name: 'Caja', to: '/cash-register', show: canAccessCashRegister.value },
  { name: 'Usuarios', to: '/users', show: canManageUsers.value },
  { name: 'Suscripción', to: '/subscription', show: canViewSubscription.value }
].filter(item => item.show));
</script>
```

---

### 5. Mejorar Validaciones de Formularios
**Estado:** ⬜ Pendiente

**Descripción:**
Aplicar el módulo de validaciones a todos los formularios de la aplicación.

**Formularios a actualizar:**
- [ ] UserFormModal.vue - Usar validateEmail, validatePassword
- [ ] MenuItemForm.vue - Usar validatePrice, validateRequired
- [ ] CategoryForm.vue - Usar validateRequired, validateName
- [ ] TableForm.vue - Usar validateRequired, validateNumeric
- [ ] LoginView.vue - Usar validateEmail, validatePassword
- [ ] RegisterView.vue - Usar todas las validaciones

**Beneficios:**
- Validaciones consistentes
- Mensajes de error uniformes
- Código reutilizable
- Fácil de mantener

---

## 🟢 Baja Prioridad

### 6. Sistema de Notificaciones de Permisos
**Estado:** ⬜ Pendiente

**Descripción:**
Mostrar notificaciones cuando un usuario intenta acceder a algo sin permisos.

**Tareas:**
- [ ] Crear composable useNotifications
- [ ] Agregar toast/notification cuando se bloquea acceso
- [ ] Agregar mensajes personalizados por tipo de permiso
- [ ] Agregar sugerencias (ej: "Contacta al administrador")

---

### 7. Analytics de Permisos
**Estado:** ⬜ Pendiente

**Descripción:**
Registrar intentos de acceso no autorizado para análisis de seguridad.

**Tareas:**
- [ ] Crear servicio de analytics
- [ ] Registrar intentos fallidos de acceso a rutas
- [ ] Registrar intentos fallidos de acceso a endpoints
- [ ] Dashboard de seguridad para sysadmin
- [ ] Alertas de intentos sospechosos

---

### 8. Tests de Permisos
**Estado:** ⬜ Pendiente

**Descripción:**
Crear suite completa de tests para el sistema de permisos.

**Tareas:**
- [ ] Tests unitarios de funciones de permisos
- [ ] Tests de router guards
- [ ] Tests de componentes con permisos
- [ ] Tests E2E de flujos completos por rol
- [ ] Tests de endpoints protegidos en backend

---

### 9. Documentación de Usuario
**Estado:** ⬜ Pendiente

**Descripción:**
Crear documentación para usuarios finales sobre roles y permisos.

**Tareas:**
- [ ] Guía de roles y responsabilidades
- [ ] FAQ sobre permisos
- [ ] Videos tutoriales por rol
- [ ] Manual de administrador

---

### 10. Mejoras de UX
**Estado:** ⬜ Pendiente

**Descripción:**
Mejorar la experiencia de usuario relacionada con permisos.

**Tareas:**
- [ ] Tooltips explicando por qué un botón está deshabilitado
- [ ] Páginas de "Sin permisos" personalizadas
- [ ] Onboarding por rol
- [ ] Badges visuales de rol en UI

---

## ✅ Completado

### ✓ Módulo de Validaciones Reutilizable
**Estado:** ✅ Completado

**Archivos creados:**
- `frontend/src/utils/permissions.ts`
- `frontend/src/utils/validators.ts`
- `frontend/src/composables/usePermissions.ts`
- `VALIDATION_MODULE_GUIDE.md`

---

### ✓ Protección de Rutas con Módulo de Permisos
**Estado:** ✅ Completado

**Archivos modificados:**
- `frontend/src/routes.ts`
- `frontend/src/router.ts`
- `ROUTE_PERMISSIONS_GUIDE.md`

---

### ✓ Protección de Vista de Menú
**Estado:** ✅ Completado

**Archivos modificados:**
- `frontend/src/components/menu/MenuList.vue`
- `MENU_ROLE_BASED_ACCESS.md`

---

### ✓ Protección de Vista de Suscripción
**Estado:** ✅ Completado

**Archivos modificados:**
- `frontend/src/App.vue`
- `frontend/src/routes.ts`
- `SUBSCRIPTION_ACCESS_RESTRICTION.md`

---

## 📋 Resumen de Progreso

**Total de tareas:** 10
- ✅ Completadas: 4 (40%)
- 🔴 Alta prioridad: 2
- 🟡 Media prioridad: 3
- 🟢 Baja prioridad: 5

---

## 🎯 Próximos Pasos Recomendados

1. **Implementar sub-roles de staff** (Alta prioridad)
   - Impacto: Alto
   - Esfuerzo: Medio
   - Dependencias: Ninguna

2. **Proteger endpoints del backend** (Alta prioridad)
   - Impacto: Crítico (seguridad)
   - Esfuerzo: Medio
   - Dependencias: Ninguna

3. **Aplicar permisos a otras vistas** (Media prioridad)
   - Impacto: Alto
   - Esfuerzo: Bajo
   - Dependencias: Ninguna

---

## 📝 Notas

- El sistema de permisos está completamente funcional y listo para extenderse
- La arquitectura es escalable y mantenible
- Todos los cambios futuros seguirán el mismo patrón establecido
- La documentación está completa y actualizada
