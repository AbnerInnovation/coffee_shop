"""
Script de diagnóstico para verificar sesiones de caja registradora
Ejecutar con: python diagnose_sessions.py
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/coffee_shop")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def diagnose_sessions():
    """Diagnose cash register sessions and their restaurant associations"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("DIAGNÓSTICO DE SESIONES DE CAJA REGISTRADORA")
        print("="*80 + "\n")
        
        # 1. Check all restaurants
        print("1. RESTAURANTES EN EL SISTEMA:")
        print("-" * 80)
        restaurants = db.execute(text("""
            SELECT id, name, subdomain, created_at
            FROM restaurants
            ORDER BY id
        """)).fetchall()
        
        for r in restaurants:
            print(f"   ID: {r[0]:3d} | Nombre: {r[1]:30s} | Subdomain: {r[2]:20s} | Creado: {r[3]}")
        
        print(f"\n   Total de restaurantes: {len(restaurants)}\n")
        
        # 2. Check all sessions
        print("2. TODAS LAS SESIONES DE CAJA:")
        print("-" * 80)
        sessions = db.execute(text("""
            SELECT 
                s.id,
                s.restaurant_id,
                r.name as restaurant_name,
                s.session_number,
                s.status,
                s.opened_at,
                s.closed_at
            FROM cash_register_sessions s
            LEFT JOIN restaurants r ON s.restaurant_id = r.id
            ORDER BY s.id DESC
            LIMIT 50
        """)).fetchall()
        
        for s in sessions:
            status = s[4] if s[4] else "UNKNOWN"
            restaurant_name = s[2] if s[2] else "⚠️  RESTAURANTE NO EXISTE"
            print(f"   Session ID: {s[0]:3d} | Restaurant ID: {s[1]:3d} | {restaurant_name:30s} | #: {s[3]:3d} | Status: {status:10s}")
        
        print(f"\n   Total de sesiones: {len(sessions)}\n")
        
        # 3. Check orphaned sessions (sessions without restaurant)
        print("3. SESIONES HUÉRFANAS (sin restaurante válido):")
        print("-" * 80)
        orphaned = db.execute(text("""
            SELECT 
                s.id,
                s.restaurant_id,
                s.session_number,
                s.status,
                s.opened_at
            FROM cash_register_sessions s
            LEFT JOIN restaurants r ON s.restaurant_id = r.id
            WHERE r.id IS NULL
        """)).fetchall()
        
        if orphaned:
            for o in orphaned:
                print(f"   ⚠️  Session ID: {o[0]:3d} | Restaurant ID inválido: {o[1]:3d} | Session #: {o[2]:3d} | Status: {o[3]}")
            print(f"\n   ⚠️  PROBLEMA: {len(orphaned)} sesiones huérfanas encontradas")
        else:
            print("   ✅ No hay sesiones huérfanas")
        
        print()
        
        # 4. Check sessions per restaurant
        print("4. SESIONES POR RESTAURANTE:")
        print("-" * 80)
        per_restaurant = db.execute(text("""
            SELECT 
                r.id,
                r.name,
                COUNT(s.id) as total_sessions,
                SUM(CASE WHEN s.status = 'OPEN' THEN 1 ELSE 0 END) as open_sessions,
                SUM(CASE WHEN s.status = 'CLOSED' THEN 1 ELSE 0 END) as closed_sessions
            FROM restaurants r
            LEFT JOIN cash_register_sessions s ON r.id = s.restaurant_id
            GROUP BY r.id, r.name
            ORDER BY r.id
        """)).fetchall()
        
        for p in per_restaurant:
            print(f"   Restaurant ID: {p[0]:3d} | {p[1]:30s} | Total: {p[2]:3d} | Abiertas: {p[3]:3d} | Cerradas: {p[4]:3d}")
        
        print()
        
        # 5. Check for duplicate session numbers per restaurant
        print("5. VERIFICAR NÚMEROS DE SESIÓN DUPLICADOS:")
        print("-" * 80)
        duplicates = db.execute(text("""
            SELECT 
                restaurant_id,
                session_number,
                COUNT(*) as count
            FROM cash_register_sessions
            GROUP BY restaurant_id, session_number
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicates:
            for d in duplicates:
                print(f"   ⚠️  Restaurant ID: {d[0]:3d} | Session #: {d[1]:3d} | Duplicados: {d[2]}")
            print(f"\n   ⚠️  PROBLEMA: {len(duplicates)} números de sesión duplicados")
        else:
            print("   ✅ No hay números de sesión duplicados")
        
        print("\n" + "="*80)
        print("DIAGNÓSTICO COMPLETADO")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {e}\n")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_sessions()
