#!/bin/bash

################################################################################
# Script de Deployment Automatizado para AWS EC2
# Coffee Shop Admin - Backend
# 
# Uso: ./backend/deploy-ec2.sh
################################################################################

set -e  # Exit on error

# Trap para manejar interrupciones
cleanup() {
    echo ""
    warning "⚠️  Deployment interrumpido!"
    warning "Si el deployment estaba en progreso, revisa el estado del servicio"
    warning "Log guardado en: $LOG_FILE"
    exit 130
}
trap cleanup SIGINT SIGTERM

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables de configuración
PROJECT_DIR="/home/ubuntu/coffee-shop"
BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/home/ubuntu/deployment_${DATE}.log"

# Funciones de utilidad
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

# Verificar que estamos en el servidor correcto
check_environment() {
    log "Verificando entorno..."
    
    if [ ! -d "$PROJECT_DIR" ]; then
        error "Directorio del proyecto no encontrado: $PROJECT_DIR"
        exit 1
    fi
    
    # Verificar permisos de escritura para logs
    if ! touch "$LOG_FILE" 2>/dev/null; then
        error "No se puede escribir en: $LOG_FILE"
        error "Verifica permisos en /home/ubuntu/"
        exit 1
    fi
    
    success "Entorno verificado"
}

# Paso 1: Conectarse al servidor (ya estamos conectados si ejecutamos esto)
step1_connection() {
    log "=========================================="
    log "PASO 1: Verificando conexión"
    log "=========================================="
    
    log "Usuario: $(whoami)"
    log "Directorio: $(pwd)"
    log "Hostname: $(hostname)"
    
    success "Paso 1 completado"
}

# Paso 2: Backup
step2_backup() {
    log "=========================================="
    log "PASO 2: Creando backup"
    log "=========================================="
    
    # Crear directorio de backups si no existe
    mkdir -p "$BACKUP_DIR"
    
    # Backup del código
    log "Creando backup del código..."
    if [ -d "$PROJECT_DIR/backend" ]; then
        cp -r "$PROJECT_DIR/backend" "$BACKUP_DIR/backend_$DATE"
        success "Backup del código creado: $BACKUP_DIR/backend_$DATE"
    else
        error "Directorio backend no encontrado"
        exit 1
    fi
    
    # Backup de requirements.txt
    if [ -f "$PROJECT_DIR/backend/requirements.txt" ]; then
        cp "$PROJECT_DIR/backend/requirements.txt" "$PROJECT_DIR/backend/requirements.txt.backup"
        success "Backup de requirements.txt creado"
    fi
    
    # Backup de base de datos (opcional)
    # Descomentar si quieres backup de DB
    # log "Creando backup de base de datos..."
    # pg_dump -U postgres coffee_shop > "$BACKUP_DIR/db_backup_$DATE.sql"
    
    success "Paso 2 completado"
}

# Paso 3: Pull de cambios
step3_git_pull() {
    log "=========================================="
    log "PASO 3: Actualizando código desde Git"
    log "=========================================="
    
    cd "$PROJECT_DIR"
    
    # Verificar rama actual
    CURRENT_BRANCH=$(git branch --show-current)
    log "Rama actual: $CURRENT_BRANCH"
    
    # Stash cambios locales si los hay
    if ! git diff-index --quiet HEAD --; then
        warning "Hay cambios locales, haciendo stash..."
        git stash
    fi
    
    # Pull desde la rama actual
    log "Ejecutando git pull..."
    if git pull origin "$CURRENT_BRANCH"; then
        success "Git pull exitoso"
        
        # Mostrar últimos commits
        log "Últimos commits:"
        git log -3 --oneline | tee -a "$LOG_FILE"
    else
        error "Git pull falló"
        exit 1
    fi
    
    success "Paso 3 completado"
}

# Paso 4: Activar entorno virtual
step4_activate_venv() {
    log "=========================================="
    log "PASO 4: Activando entorno virtual"
    log "=========================================="
    
    cd "$PROJECT_DIR/backend"
    
    if [ ! -d "venv" ]; then
        error "Entorno virtual no encontrado"
        exit 1
    fi
    
    # Activar venv (permanecerá activo para todos los pasos siguientes)
    source venv/bin/activate
    
    # Verificar
    PYTHON_PATH=$(which python)
    log "Python path: $PYTHON_PATH"
    
    if [[ "$PYTHON_PATH" == *"venv"* ]]; then
        success "Entorno virtual activado correctamente"
        log "El venv permanecerá activo para los siguientes pasos"
    else
        error "Entorno virtual no se activó correctamente"
        exit 1
    fi
    
    success "Paso 4 completado"
}

# Paso 5: Actualizar dependencias
step5_update_dependencies() {
    log "=========================================="
    log "PASO 5: Actualizando dependencias"
    log "=========================================="
    
    cd "$PROJECT_DIR/backend"
    
    # Actualizar pip
    log "Actualizando pip..."
    python -m pip install --upgrade pip
    
    # Instalar dependencias
    log "Instalando dependencias desde requirements.txt..."
    if pip install -r requirements.txt; then
        success "Dependencias instaladas correctamente"
    else
        error "Falló la instalación de dependencias"
        exit 1
    fi
    
    # Verificar versiones críticas
    log "Verificando versiones críticas..."
    echo "" | tee -a "$LOG_FILE"
    pip show fastapi | grep Version | tee -a "$LOG_FILE" || warning "fastapi no encontrado"
    pip show starlette | grep Version | tee -a "$LOG_FILE" || warning "starlette no encontrado"
    pip show python-jose | grep Version | tee -a "$LOG_FILE" || warning "python-jose no encontrado"
    pip show python-multipart | grep Version | tee -a "$LOG_FILE" || warning "python-multipart no encontrado"
    pip show h11 | grep Version | tee -a "$LOG_FILE" || warning "h11 no encontrado"
    echo "" | tee -a "$LOG_FILE"
    
    success "Paso 5 completado"
}

# Paso 6: Ejecutar migraciones de base de datos
step6_run_migrations() {
    log "=========================================="
    log "PASO 6: Ejecutando migraciones de base de datos"
    log "=========================================="
    
    cd "$PROJECT_DIR/backend"
    
    # Verificar si alembic está instalado
    if ! command -v alembic &> /dev/null; then
        warning "Alembic no está instalado, saltando migraciones"
        return 0
    fi
    
    # Verificar si hay directorio de migraciones
    if [ ! -d "migrations" ] && [ ! -d "alembic" ]; then
        warning "Directorio de migraciones no encontrado, saltando"
        return 0
    fi
    
    log "Ejecutando migraciones con Alembic..."
    if alembic upgrade head; then
        success "Migraciones ejecutadas correctamente"
    else
        error "Falló la ejecución de migraciones"
        warning "Revisa los logs de Alembic para más detalles"
        
        # Preguntar si continuar
        read -p "¿Deseas continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment cancelado por el usuario"
            exit 1
        fi
    fi
    
    # Mostrar versión actual de la base de datos
    log "Versión actual de la base de datos:"
    alembic current | tee -a "$LOG_FILE" || warning "No se pudo obtener la versión actual"
    
    success "Paso 6 completado"
}

# Paso 7: Ejecutar tests
step7_run_tests() {
    log "=========================================="
    log "PASO 7: Ejecutando tests"
    log "=========================================="
    
    cd "$PROJECT_DIR/backend"
    
    # Verificar si pytest está instalado
    if ! command -v pytest &> /dev/null; then
        warning "pytest no está instalado, saltando tests"
        return 0
    fi
    
    log "Ejecutando suite de tests..."
    if pytest -v; then
        success "Todos los tests pasaron"
    else
        error "Tests fallaron"
        warning "Se recomienda NO continuar con el deployment"
        
        # Preguntar si continuar
        read -p "¿Deseas continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment cancelado por el usuario"
            exit 1
        fi
    fi
    
    success "Paso 7 completado"
}

# Paso 8: Reiniciar servicio
step8_restart_service() {
    log "=========================================="
    log "PASO 8: Reiniciando servicio"
    log "=========================================="
    
    # Detectar qué sistema de gestión de procesos se usa
    if systemctl is-active --quiet fastapi-2 2>/dev/null; then
        log "Usando Systemd..."
        
        # Reiniciar
        log "Reiniciando fastapi-2..."
        if sudo systemctl restart fastapi-2; then
            success "Servicio reiniciado con Systemd"
            
            # Esperar un poco
            sleep 3
            
            # Verificar estado
            sudo systemctl status fastapi-2 --no-pager | tee -a "$LOG_FILE"
        else
            error "Falló el reinicio con Systemd"
            exit 1
        fi
        
    elif command -v pm2 &> /dev/null; then
        log "Usando PM2..."
        
        # Listar procesos
        pm2 list | tee -a "$LOG_FILE"
        
        # Reiniciar
        log "Reiniciando fastapi-2..."
        if pm2 restart fastapi-2; then
            success "Servicio reiniciado con PM2"
            
            # Esperar un poco
            sleep 3
            
            # Verificar estado
            pm2 status fastapi-2 | tee -a "$LOG_FILE"
        else
            error "Falló el reinicio con PM2"
            exit 1
        fi
        
    else
        warning "No se detectó Systemd ni PM2"
        warning "Por favor reinicia el servicio manualmente"
    fi
    
    success "Paso 8 completado"
}

# Verificación post-deployment
verify_deployment() {
    log "=========================================="
    log "VERIFICACIÓN POST-DEPLOYMENT"
    log "=========================================="
    
    # Esperar un poco para que el servicio inicie
    log "Esperando 5 segundos para que el servicio inicie..."
    sleep 5
    
    # Health check
    log "Ejecutando health check..."
    if command -v curl &> /dev/null; then
        if curl -f http://localhost:8001/api/v1/health 2>/dev/null; then
            echo "" | tee -a "$LOG_FILE"
            success "Health check exitoso"
        else
            echo "" | tee -a "$LOG_FILE"
            error "Health check falló"
            warning "El servicio puede no estar funcionando correctamente"
        fi
    else
        warning "curl no está instalado, saltando health check"
        log "Verifica manualmente: curl http://localhost:8001/api/v1/health"
    fi
    
    # Verificar logs recientes
    log "Últimas líneas de logs:"
    if systemctl is-active --quiet fastapi-2 2>/dev/null; then
        sudo journalctl -u fastapi-2 -n 20 --no-pager | tee -a "$LOG_FILE" || warning "No se pudieron obtener logs de systemd"
    elif command -v pm2 &> /dev/null; then
        pm2 logs fastapi-2 --lines 20 --nostream 2>/dev/null | tee -a "$LOG_FILE" || warning "No se pudieron obtener logs de PM2"
    else
        warning "No se pudo determinar el sistema de logs"
    fi
}

# Resumen final
final_summary() {
    log "=========================================="
    log "RESUMEN DEL DEPLOYMENT"
    log "=========================================="
    
    success "Deployment completado exitosamente"
    log "Fecha: $(date)"
    log "Backup: $BACKUP_DIR/backend_$DATE"
    log "Log: $LOG_FILE"
    
    echo ""
    log "Próximos pasos recomendados:"
    log "1. Monitorear logs por 10-15 minutos"
    log "2. Verificar endpoints críticos"
    log "3. Probar funcionalidad en el frontend"
    
    echo ""
    warning "Si algo sale mal, ejecuta el rollback:"
    log "cd $PROJECT_DIR"
    log "rm -rf backend"
    log "mv $BACKUP_DIR/backend_$DATE backend"
    log "sudo systemctl restart fastapi-2"
}

# Función principal
main() {
    log "=========================================="
    log "INICIANDO DEPLOYMENT"
    log "Coffee Shop Admin - Backend"
    log "=========================================="
    
    # Verificar entorno
    check_environment
    
    # Ejecutar pasos
    step1_connection
    step2_backup
    step3_git_pull
    step4_activate_venv
    step5_update_dependencies
    step6_run_migrations
    step7_run_tests
    step8_restart_service
    
    # Verificación
    verify_deployment
    
    # Resumen
    final_summary
    
    success "🎉 DEPLOYMENT COMPLETADO 🎉"
}

# Ejecutar
main "$@"
