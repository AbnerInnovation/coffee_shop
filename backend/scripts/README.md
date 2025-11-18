# Scripts de Utilidad - Backend

Scripts auxiliares para mantenimiento y administración del backend.

## 📜 Scripts Disponibles

### 1. `cleanup-logs.sh`
Limpia logs de deployment antiguos para mantener el directorio organizado.

**Uso:**
```bash
# Eliminar logs mayores a 30 días (por defecto)
./backend/scripts/cleanup-logs.sh

# Eliminar logs mayores a 7 días
./backend/scripts/cleanup-logs.sh 7

# Eliminar logs mayores a 90 días
./backend/scripts/cleanup-logs.sh 90
```

**Características:**
- ✅ Mantiene logs recientes
- ✅ Elimina solo archivos `deployment_*.log`
- ✅ Muestra estadísticas de limpieza
- ✅ Calcula tamaño del directorio

**Recomendación:** Ejecutar mensualmente o configurar como cron job.

---

### 2. `migrate-old-logs.sh`
Migra logs antiguos desde `/home/ubuntu/` al directorio del proyecto.

**Uso:**
```bash
# Ejecutar una sola vez después de actualizar el script de deployment
./backend/scripts/migrate-old-logs.sh
```

**Características:**
- ✅ Busca logs en `/home/ubuntu/`
- ✅ Los mueve a `/home/ubuntu/coffee-shop/logs/`
- ✅ Muestra progreso y estadísticas
- ✅ No sobrescribe archivos existentes

**Nota:** Solo necesitas ejecutar este script una vez para migrar logs antiguos.

---

## 🔧 Configuración de Cron Jobs (Opcional)

Para automatizar la limpieza de logs:

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar limpieza cada mes (día 1 a las 3 AM)
0 3 1 * * /home/ubuntu/coffee-shop/backend/scripts/cleanup-logs.sh 30
```

---

## 📁 Estructura de Logs

Después de la migración, los logs se guardan en:

```
backend/
├── logs/
│   ├── .gitkeep
│   ├── deployment_20251114_195854.log
│   ├── deployment_20251115_064028.log
│   └── ...
└── scripts/
    ├── cleanup-logs.sh
    ├── migrate-old-logs.sh
    └── README.md
```

---

## 🚀 Pasos Recomendados

1. **Migrar logs antiguos** (una sola vez):
   ```bash
   ./backend/scripts/migrate-old-logs.sh
   ```

2. **Verificar que el nuevo deployment funciona**:
   ```bash
   ./backend/deploy-ec2.sh
   # Los logs ahora se guardarán en backend/logs/
   ```

3. **Configurar limpieza automática** (opcional):
   ```bash
   crontab -e
   # Agregar cron job como se muestra arriba
   ```

---

## 📝 Notas

- Los logs NO se suben al repositorio (están en `.gitignore`)
- Solo se mantiene `.gitkeep` para preservar la estructura de carpetas
- Los logs antiguos en `/home/ubuntu/` pueden eliminarse manualmente después de la migración
- Se recomienda mantener logs de los últimos 30-90 días para auditoría
