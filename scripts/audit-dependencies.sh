#!/bin/bash

# Script para auditar dependencias de frontend y backend
# Uso: ./scripts/audit-dependencies.sh

set -e

echo "🔒 ====================================="
echo "   Security Audit - Coffee Shop Admin"
echo "====================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_header() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ==================== FRONTEND AUDIT ====================
print_header "📦 Frontend Security Audit (npm)"
echo "-----------------------------------"

cd frontend

if [ ! -d "node_modules" ]; then
    print_warning "node_modules not found. Installing dependencies..."
    npm install
fi

echo ""
print_header "Running npm audit..."
if npm audit --audit-level=moderate; then
    print_success "No moderate or higher vulnerabilities found!"
else
    print_warning "Vulnerabilities detected. See details above."
fi

echo ""
print_header "Production dependencies only:"
npm audit --production --audit-level=high || print_warning "Production vulnerabilities found"

echo ""
print_header "Generating detailed report..."
npm audit --json > ../reports/npm-audit-report.json 2>/dev/null || true
if [ -f "../reports/npm-audit-report.json" ]; then
    print_success "Report saved to reports/npm-audit-report.json"
fi

cd ..

# ==================== BACKEND AUDIT ====================
echo ""
echo ""
print_header "🐍 Backend Security Audit (pip)"
echo "-----------------------------------"

cd backend

# Verificar si pip-audit está instalado
if ! command -v pip-audit &> /dev/null; then
    print_warning "pip-audit not found. Installing..."
    pip install pip-audit
fi

echo ""
print_header "Running pip-audit..."
if pip-audit --desc; then
    print_success "No vulnerabilities found!"
else
    print_warning "Vulnerabilities detected. See details above."
fi

echo ""
print_header "Generating detailed report..."
pip-audit --format json > ../reports/pip-audit-report.json 2>/dev/null || true
if [ -f "../reports/pip-audit-report.json" ]; then
    print_success "Report saved to reports/pip-audit-report.json"
fi

cd ..

# ==================== SUMMARY ====================
echo ""
echo ""
print_header "📊 Audit Summary"
echo "-----------------------------------"

if [ -f "reports/npm-audit-report.json" ]; then
    echo ""
    echo "Frontend (npm):"
    if command -v jq &> /dev/null; then
        cat reports/npm-audit-report.json | jq -r '.metadata.vulnerabilities | 
            "  Total: \(.total)\n  Critical: \(.critical)\n  High: \(.high)\n  Moderate: \(.moderate)\n  Low: \(.low)"'
    else
        print_warning "Install jq for better JSON parsing"
    fi
fi

if [ -f "reports/pip-audit-report.json" ]; then
    echo ""
    echo "Backend (pip):"
    if command -v jq &> /dev/null; then
        VULN_COUNT=$(cat reports/pip-audit-report.json | jq '. | length')
        echo "  Total vulnerabilities: $VULN_COUNT"
    else
        print_warning "Install jq for better JSON parsing"
    fi
fi

echo ""
print_header "✨ Audit complete!"
echo ""
echo "Reports saved in: ./reports/"
echo "  - npm-audit-report.json"
echo "  - pip-audit-report.json"
echo ""
