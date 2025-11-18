#!/bin/bash

################################################################################
# Script de Limpieza de Logs Antiguos
# Coffee Shop Admin - Backend
# 
# Uso: ./backend/scripts/cleanup-logs.sh [días]
# Ejemplo: ./backend/scripts/cleanup-logs.sh 30  (elimina logs mayores a 30 días)
################################################################################

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Días por defecto (mantener logs de los últimos 30 días)
DAYS=${1:-30}

# Directorio de logs
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"

echo -e "${YELLOW}🧹 Limpiando logs antiguos...${NC}"
echo "Directorio: $LOG_DIR"
echo "Eliminando logs mayores a $DAYS días"
echo ""

# Verificar que el directorio existe
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directorio de logs no encontrado: $LOG_DIR${NC}"
    exit 0
fi

# Contar archivos antes
BEFORE=$(find "$LOG_DIR" -name "deployment_*.log" -type f | wc -l)

# Eliminar logs antiguos
find "$LOG_DIR" -name "deployment_*.log" -type f -mtime +$DAYS -delete

# Contar archivos después
AFTER=$(find "$LOG_DIR" -name "deployment_*.log" -type f | wc -l)
DELETED=$((BEFORE - AFTER))

echo -e "${GREEN}✅ Limpieza completada${NC}"
echo "Logs eliminados: $DELETED"
echo "Logs restantes: $AFTER"
echo ""

# Mostrar tamaño del directorio
if command -v du &> /dev/null; then
    SIZE=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)
    echo "Tamaño total del directorio de logs: $SIZE"
fi
