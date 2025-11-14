# Script para auditar dependencias de frontend y backend en Windows
# Uso: .\scripts\audit-dependencies.ps1

Write-Host "🔒 =====================================" -ForegroundColor Blue
Write-Host "   Security Audit - Coffee Shop Admin" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue
Write-Host ""

# Crear directorio de reportes si no existe
if (-not (Test-Path "reports")) {
    New-Item -ItemType Directory -Path "reports" | Out-Null
}

# ==================== FRONTEND AUDIT ====================
Write-Host "📦 Frontend Security Audit (npm)" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "Running npm audit..." -ForegroundColor Cyan
try {
    npm audit --audit-level=moderate
    Write-Host "✅ No moderate or higher vulnerabilities found!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Vulnerabilities detected. See details above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Production dependencies only:" -ForegroundColor Cyan
try {
    npm audit --production --audit-level=high
} catch {
    Write-Host "⚠️  Production vulnerabilities found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Generating detailed report..." -ForegroundColor Cyan
npm audit --json > ..\reports\npm-audit-report.json 2>$null
if (Test-Path "..\reports\npm-audit-report.json") {
    Write-Host "✅ Report saved to reports\npm-audit-report.json" -ForegroundColor Green
}

Set-Location ..

# ==================== BACKEND AUDIT ====================
Write-Host ""
Write-Host ""
Write-Host "🐍 Backend Security Audit (pip)" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

Set-Location backend

# Verificar si pip-audit está instalado
$pipAuditInstalled = pip list | Select-String "pip-audit"
if (-not $pipAuditInstalled) {
    Write-Host "⚠️  pip-audit not found. Installing..." -ForegroundColor Yellow
    pip install pip-audit
}

Write-Host ""
Write-Host "Running pip-audit..." -ForegroundColor Cyan
try {
    pip-audit --desc
    Write-Host "✅ No vulnerabilities found!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Vulnerabilities detected. See details above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Generating detailed report..." -ForegroundColor Cyan
pip-audit --format json > ..\reports\pip-audit-report.json 2>$null
if (Test-Path "..\reports\pip-audit-report.json") {
    Write-Host "✅ Report saved to reports\pip-audit-report.json" -ForegroundColor Green
}

Set-Location ..

# ==================== SUMMARY ====================
Write-Host ""
Write-Host ""
Write-Host "📊 Audit Summary" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

if (Test-Path "reports\npm-audit-report.json") {
    Write-Host ""
    Write-Host "Frontend (npm):" -ForegroundColor White
    $npmReport = Get-Content "reports\npm-audit-report.json" | ConvertFrom-Json
    $vulns = $npmReport.metadata.vulnerabilities
    Write-Host "  Total: $($vulns.total)" -ForegroundColor White
    Write-Host "  Critical: $($vulns.critical)" -ForegroundColor $(if ($vulns.critical -gt 0) { "Red" } else { "Gray" })
    Write-Host "  High: $($vulns.high)" -ForegroundColor $(if ($vulns.high -gt 0) { "Red" } else { "Gray" })
    Write-Host "  Moderate: $($vulns.moderate)" -ForegroundColor $(if ($vulns.moderate -gt 0) { "Yellow" } else { "Gray" })
    Write-Host "  Low: $($vulns.low)" -ForegroundColor Gray
}

if (Test-Path "reports\pip-audit-report.json") {
    Write-Host ""
    Write-Host "Backend (pip):" -ForegroundColor White
    $pipReport = Get-Content "reports\pip-audit-report.json" | ConvertFrom-Json
    $vulnCount = $pipReport.Count
    Write-Host "  Total vulnerabilities: $vulnCount" -ForegroundColor $(if ($vulnCount -gt 0) { "Yellow" } else { "Green" })
}

Write-Host ""
Write-Host "✨ Audit complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Reports saved in: .\reports\" -ForegroundColor Cyan
Write-Host "  - npm-audit-report.json" -ForegroundColor Gray
Write-Host "  - pip-audit-report.json" -ForegroundColor Gray
Write-Host ""
