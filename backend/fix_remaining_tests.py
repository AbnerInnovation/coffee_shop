"""Script para agregar created_by_user_id a todos los CashTransactionCreate"""
import re
from pathlib import Path

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Patrón: CashTransactionCreate( ... payment_method=... ) sin created_by_user_id
    # Buscar bloques que NO tengan created_by_user_id
    pattern = r'(CashTransactionCreate\([^)]*?payment_method=PaymentMethod\.\w+)\s*\)'
    
    def add_created_by(match):
        block = match.group(1)
        if 'created_by_user_id' in block:
            return match.group(0)  # Ya tiene, no cambiar
        return block + ',\n            created_by_user_id=test_admin_user.id\n        )'
    
    content = re.sub(pattern, add_created_by, content, flags=re.DOTALL)
    
    # Casos sin payment_method
    pattern2 = r'(CashTransactionCreate\([^)]*?description="[^"]+")(\s*\))'
    
    def add_created_by2(match):
        block = match.group(1)
        closing = match.group(2)
        if 'created_by_user_id' in block or 'payment_method' in block:
            return match.group(0)
        return block + ',\n            created_by_user_id=test_admin_user.id' + closing
    
    content = re.sub(pattern2, add_created_by2, content, flags=re.DOTALL)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Archivos a corregir
files = [
    'tests/services/cash_register/test_transaction_service.py',
    'tests/services/cash_register/test_report_service.py',
]

for file in files:
    path = Path(file)
    if path.exists():
        if fix_file(path):
            print(f'✅ {file}')
        else:
            print(f'ℹ️  {file} - sin cambios')
    else:
        print(f'❌ {file} - no encontrado')
