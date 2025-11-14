# Script para corregir vulnerabilidades detectadas
# Uso: .\scripts\fix-vulnerabilities.ps1

Write-Host "🔒 =====================================" -ForegroundColor Red
Write-Host "   Fixing Security Vulnerabilities" -ForegroundColor Red
Write-Host "=====================================" -ForegroundColor Red
Write-Host ""

# Backup requirements.txt
Write-Host "📦 Creating backup of requirements.txt..." -ForegroundColor Cyan
Copy-Item "backend\requirements.txt" "backend\requirements.txt.backup"
Write-Host "✅ Backup created: backend\requirements.txt.backup" -ForegroundColor Green
Write-Host ""

# Actualizar dependencias críticas
Write-Host "🔧 Updating critical dependencies..." -ForegroundColor Cyan
Write-Host ""

Set-Location backend

# Vulnerabilidades CRÍTICAS
Write-Host "1. Updating python-jose (CVE-2024-33663, CVE-2024-33664)..." -ForegroundColor Yellow
pip install --upgrade "python-jose[cryptography]>=3.4.0"

Write-Host "2. Updating starlette (CVE-2024-47874, CVE-2025-54121)..." -ForegroundColor Yellow
pip install --upgrade "starlette>=0.47.2"

Write-Host "3. Updating python-multipart (CVE-2024-24762, CVE-2024-53981)..." -ForegroundColor Yellow
pip install --upgrade "python-multipart>=0.0.18"

Write-Host "4. Updating fastapi (CVE-2024-24762)..." -ForegroundColor Yellow
pip install --upgrade "fastapi>=0.109.1"

Write-Host "5. Updating h11 (CVE-2025-43859)..." -ForegroundColor Yellow
pip install --upgrade "h11>=0.16.0"

Write-Host ""
Write-Host "🟡 Updating moderate priority dependencies..." -ForegroundColor Cyan
Write-Host ""

Write-Host "6. Updating pymysql (CVE-2024-36039)..." -ForegroundColor Yellow
pip install --upgrade "pymysql>=1.1.1"

Write-Host "7. Updating pip (CVE-2025-8869)..." -ForegroundColor Yellow
python -m pip install --upgrade "pip>=25.3"

Write-Host "8. Updating urllib3 (CVE-2025-50181)..." -ForegroundColor Yellow
pip install --upgrade "urllib3>=2.5.0"

Write-Host ""
Write-Host "📝 Generating new requirements.txt..." -ForegroundColor Cyan
pip freeze > requirements.txt
Write-Host "✅ requirements.txt updated" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "🧪 Running tests to verify updates..." -ForegroundColor Cyan
Set-Location backend
pytest
Set-Location ..

Write-Host ""
Write-Host "🔍 Running new security audit..." -ForegroundColor Cyan
.\scripts\audit-dependencies.ps1

Write-Host ""
Write-Host "✅ Vulnerability fixes complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "  1. Review the new requirements.txt" -ForegroundColor White
Write-Host "  2. Test the application thoroughly" -ForegroundColor White
Write-Host "  3. Commit changes: git add backend/requirements.txt" -ForegroundColor White
Write-Host "  4. Deploy to production" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Note about ecdsa vulnerability:" -ForegroundColor Yellow
Write-Host "  CVE-2024-23342 in ecdsa has no fix available." -ForegroundColor White
Write-Host "  Consider migrating to 'cryptography' library for JWT operations." -ForegroundColor White
Write-Host ""
