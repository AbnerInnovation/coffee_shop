"""
Seed script for subscription plans and add-ons.
Run this after creating the database migration.

Usage:
    python seed_subscription_plans.py
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.base import SessionLocal
from app.models import (
    SubscriptionPlan, PlanTier,
    SubscriptionAddon, AddonType, AddonCategory
)

def seed_plans(db):
    """Seed subscription plans"""
    
    plans_data = [
        {
            "name": "trial",
            "tier": PlanTier.TRIAL,
            "display_name": "Prueba Gratuita",
            "description": "14 días de prueba con acceso completo al Plan Pro",
            "monthly_price": 0.0,
            "annual_price": 0.0,
            "max_admin_users": 1,
            "max_waiter_users": 4,
            "max_cashier_users": 2,
            "max_kitchen_users": 2,
            "max_owner_users": 0,
            "max_tables": 35,
            "max_menu_items": 400,
            "max_categories": 20,
            "has_kitchen_module": True,
            "has_ingredients_module": True,
            "has_inventory_module": False,
            "has_advanced_reports": True,
            "has_multi_branch": False,
            "has_priority_support": False,
            "report_retention_days": 60,
            "support_hours_monthly": 0.0,
            "is_trial": True,
            "trial_duration_days": 14,
            "is_popular": False,
            "is_active": True,
            "sort_order": 0,
            "features": {
                "trial_limitations": [
                    "Acceso completo por 14 días",
                    "Sin tarjeta de crédito requerida",
                    "Datos se conservan al actualizar",
                    "Límite de 35 mesas",
                    "Límite de 400 productos"
                ]
            }
        },
        {
            "name": "starter",
            "tier": PlanTier.STARTER,
            "display_name": "Starter",
            "description": "Ideal para food trucks, cafeterías pequeñas y negocios iniciando",
            "monthly_price": 399.0,
            "annual_price": 3591.0,  # 25% discount (299.25/month)
            "max_admin_users": 1,
            "max_waiter_users": 2,
            "max_cashier_users": 0,
            "max_kitchen_users": 0,
            "max_owner_users": 0,
            "max_tables": 10,
            "max_menu_items": 50,
            "max_categories": 10,
            "has_kitchen_module": False,
            "has_ingredients_module": False,
            "has_inventory_module": False,
            "has_advanced_reports": False,
            "has_multi_branch": False,
            "has_priority_support": False,
            "report_retention_days": 7,
            "support_hours_monthly": 0.0,
            "is_trial": False,
            "trial_duration_days": 14,
            "is_popular": False,
            "is_active": True,
            "sort_order": 1,
            "features": {
                "included": [
                    "Módulos básicos: Mesas, Pedidos, Menú, Caja",
                    "Reportes básicos (7 días)",
                    "Soporte por WhatsApp"
                ],
                "not_included": [
                    "Módulo de Cocina",
                    "Módulo de Ingredientes",
                    "Inventario",
                    "Reportes avanzados"
                ]
            }
        },
        {
            "name": "basic",
            "tier": PlanTier.BASIC,
            "display_name": "Básico",
            "description": "Ideal para taquerías, fondas y restaurantes pequeños",
            "monthly_price": 699.0,
            "annual_price": 6291.0,  # 25% discount (524.25/month)
            "max_admin_users": 1,
            "max_waiter_users": 3,
            "max_cashier_users": 0,
            "max_kitchen_users": 1,
            "max_owner_users": 0,
            "max_tables": 20,
            "max_menu_items": 150,
            "max_categories": 15,
            "has_kitchen_module": True,
            "has_ingredients_module": True,
            "has_inventory_module": False,
            "has_advanced_reports": False,
            "has_multi_branch": False,
            "has_priority_support": False,
            "report_retention_days": 15,
            "support_hours_monthly": 0.0,
            "is_trial": False,
            "trial_duration_days": 14,
            "is_popular": False,
            "is_active": True,
            "sort_order": 2,
            "features": {
                "included": [
                    "Todos los módulos básicos + Cocina",
                    "Módulo de Ingredientes incluido",
                    "Reportes básicos (15 días)",
                    "Soporte por WhatsApp"
                ],
                "value_added": "Módulo de ingredientes ($199 valor)"
            }
        },
        {
            "name": "pro",
            "tier": PlanTier.PRO,
            "display_name": "Pro",
            "description": "Restaurantes familiares y negocios en crecimiento",
            "monthly_price": 999.0,
            "annual_price": 8991.0,  # 25% discount (749.25/month)
            "max_admin_users": 1,
            "max_waiter_users": 4,
            "max_cashier_users": 2,
            "max_kitchen_users": 2,
            "max_owner_users": 0,
            "max_tables": 35,
            "max_menu_items": 400,
            "max_categories": 25,
            "has_kitchen_module": True,
            "has_ingredients_module": True,
            "has_inventory_module": False,
            "has_advanced_reports": True,
            "has_multi_branch": False,
            "has_priority_support": False,
            "report_retention_days": 60,
            "support_hours_monthly": 0.5,
            "is_trial": False,
            "trial_duration_days": 14,
            "is_popular": True,
            "is_active": True,
            "sort_order": 3,
            "features": {
                "included": [
                    "Todos los módulos básicos",
                    "Módulo de Ingredientes incluido",
                    "Reportes Avanzados incluidos",
                    "30 minutos de soporte mensual",
                    "Reportes (60 días)"
                ],
                "value_added": "Ingredientes + Reportes Avanzados ($348 valor)"
            }
        },
        {
            "name": "business",
            "tier": PlanTier.BUSINESS,
            "display_name": "Business",
            "description": "Restaurantes establecidos con múltiples turnos",
            "monthly_price": 1499.0,
            "annual_price": 13491.0,  # 25% discount (1124.25/month)
            "max_admin_users": 2,
            "max_waiter_users": 8,
            "max_cashier_users": 3,
            "max_kitchen_users": 3,
            "max_owner_users": 0,
            "max_tables": 60,
            "max_menu_items": 800,
            "max_categories": 40,
            "has_kitchen_module": True,
            "has_ingredients_module": True,
            "has_inventory_module": True,
            "has_advanced_reports": True,
            "has_multi_branch": False,
            "has_priority_support": True,
            "report_retention_days": 180,
            "support_hours_monthly": 1.5,
            "is_trial": False,
            "trial_duration_days": 14,
            "is_popular": False,
            "is_active": True,
            "sort_order": 4,
            "features": {
                "included": [
                    "Todos los módulos incluidos",
                    "Inventario incluido",
                    "1.5 horas de soporte mensual",
                    "Prioridad en soporte",
                    "Reportes históricos (180 días)"
                ],
                "value_added": "Todos los módulos ($499 valor)"
            }
        },
        {
            "name": "enterprise",
            "tier": PlanTier.ENTERPRISE,
            "display_name": "Enterprise",
            "description": "Cadenas, franquicias y grupos restauranteros",
            "monthly_price": 2199.0,
            "annual_price": 19791.0,  # 25% discount (1649.25/month)
            "max_admin_users": 4,
            "max_waiter_users": 15,
            "max_cashier_users": 5,
            "max_kitchen_users": 5,
            "max_owner_users": 1,
            "max_tables": 150,
            "max_menu_items": 9999,  # Unlimited (high number)
            "max_categories": 100,
            "has_kitchen_module": True,
            "has_ingredients_module": True,
            "has_inventory_module": True,
            "has_advanced_reports": True,
            "has_multi_branch": True,
            "has_priority_support": True,
            "report_retention_days": -1,  # Unlimited
            "support_hours_monthly": 3.0,
            "is_trial": False,
            "trial_duration_days": 14,
            "is_popular": False,
            "is_active": True,
            "sort_order": 5,
            "features": {
                "included": [
                    "Todos los módulos incluidos",
                    "Productos ilimitados",
                    "Reportes históricos ilimitados",
                    "3 horas de soporte mensual",
                    "Soporte prioritario 24/7",
                    "Visión multi-sucursal",
                    "Gerente de cuenta dedicado"
                ],
                "value_added": "Paquete completo ($799 valor)"
            }
        }
    ]
    
    print("🌱 Seeding subscription plans...")
    for plan_data in plans_data:
        existing = db.query(SubscriptionPlan).filter_by(name=plan_data["name"]).first()
        if existing:
            print(f"  ⏭️  Plan '{plan_data['name']}' already exists, skipping...")
            continue
        
        plan = SubscriptionPlan(**plan_data)
        db.add(plan)
        print(f"  ✅ Created plan: {plan_data['display_name']} (${plan_data['monthly_price']}/mes)")
    
    db.commit()
    print("✅ Subscription plans seeded successfully!\n")


def seed_addons(db):
    """Seed subscription add-ons"""
    
    addons_data = [
        {
            "name": "Módulo de Inventario",
            "code": "inventory_module",
            "display_name": "Módulo de Inventario",
            "description": "Control de stock en tiempo real, alertas de inventario bajo, registro de entradas/salidas, reportes de consumo",
            "addon_type": AddonType.MODULE,
            "category": AddonCategory.INVENTORY,
            "monthly_price": 199.0,
            "is_recurring": True,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": True,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": {"exclude_tiers": ["enterprise", "business"]},
            "is_active": True,
            "is_featured": True,
            "sort_order": 1
        },
        {
            "name": "Reportes Avanzados",
            "code": "advanced_reports",
            "display_name": "Reportes Avanzados",
            "description": "Análisis de ventas por período, productos más vendidos, análisis de meseros/cajeros, exportación a Excel/PDF, gráficas y estadísticas",
            "addon_type": AddonType.MODULE,
            "category": AddonCategory.REPORTS,
            "monthly_price": 149.0,
            "is_recurring": True,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": True,
            "enables_kitchen": False,
            "available_for_plans": {"exclude_tiers": ["enterprise", "business", "pro"]},
            "is_active": True,
            "is_featured": True,
            "sort_order": 2
        },
        {
            "name": "Módulo de Cocina",
            "code": "kitchen_module",
            "display_name": "Módulo de Cocina",
            "description": "Pantalla de cocina para gestión de pedidos, priorización de platillos, control de tiempos de preparación",
            "addon_type": AddonType.MODULE,
            "category": AddonCategory.KITCHEN,
            "monthly_price": 99.0,
            "is_recurring": True,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": True,
            "available_for_plans": {"tiers": ["starter"]},
            "is_active": True,
            "is_featured": False,
            "sort_order": 3
        },
        {
            "name": "Usuario Extra",
            "code": "extra_user",
            "display_name": "Usuario Extra",
            "description": "Agrega un usuario adicional (cualquier rol: admin, mesero, cajero, cocina)",
            "addon_type": AddonType.RESOURCE,
            "category": AddonCategory.USERS,
            "monthly_price": 79.0,
            "is_recurring": True,
            "is_quantifiable": True,
            "min_quantity": 1,
            "max_quantity": None,  # Unlimited
            "provides_users": 1,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,  # Available for all plans
            "is_active": True,
            "is_featured": True,
            "sort_order": 4
        },
        {
            "name": "Paquete de 10 Mesas Extra",
            "code": "extra_tables_10",
            "display_name": "10 Mesas Extra",
            "description": "Incrementa el límite de mesas en 10 unidades",
            "addon_type": AddonType.RESOURCE,
            "category": AddonCategory.TABLES,
            "monthly_price": 39.0,
            "is_recurring": True,
            "is_quantifiable": True,
            "min_quantity": 1,
            "max_quantity": None,
            "provides_users": 0,
            "provides_tables": 10,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": {"exclude_tiers": ["enterprise"]},
            "is_active": True,
            "is_featured": False,
            "sort_order": 5
        },
        {
            "name": "Paquete de 100 Productos Extra",
            "code": "extra_products_100",
            "display_name": "100 Productos Extra",
            "description": "Incrementa el límite de productos en menú en 100 unidades",
            "addon_type": AddonType.RESOURCE,
            "category": AddonCategory.PRODUCTS,
            "monthly_price": 79.0,
            "is_recurring": True,
            "is_quantifiable": True,
            "min_quantity": 1,
            "max_quantity": None,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 100,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": {"exclude_tiers": ["enterprise"]},
            "is_active": True,
            "is_featured": False,
            "sort_order": 6
        },
        {
            "name": "Capacitación Small",
            "code": "training_small",
            "display_name": "Capacitación Small",
            "description": "1 sesión de 2 horas - Setup básico del sistema",
            "addon_type": AddonType.SERVICE,
            "category": AddonCategory.TRAINING,
            "monthly_price": 900.0,
            "is_recurring": False,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,
            "is_active": True,
            "is_featured": False,
            "sort_order": 7
        },
        {
            "name": "Capacitación Medium",
            "code": "training_medium",
            "display_name": "Capacitación Medium",
            "description": "2 sesiones - Setup completo + capacitación de equipo",
            "addon_type": AddonType.SERVICE,
            "category": AddonCategory.TRAINING,
            "monthly_price": 1300.0,
            "is_recurring": False,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,
            "is_active": True,
            "is_featured": True,
            "sort_order": 8
        },
        {
            "name": "Capacitación Large",
            "code": "training_large",
            "display_name": "Capacitación Large",
            "description": "3 sesiones - Setup completo + capacitación + seguimiento",
            "addon_type": AddonType.SERVICE,
            "category": AddonCategory.TRAINING,
            "monthly_price": 1800.0,
            "is_recurring": False,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,
            "is_active": True,
            "is_featured": False,
            "sort_order": 9
        },
        {
            "name": "Carga Inicial de Menú",
            "code": "menu_setup",
            "display_name": "Carga Inicial de Menú",
            "description": "Importación y configuración inicial de tu menú (hasta 100 productos)",
            "addon_type": AddonType.SERVICE,
            "category": AddonCategory.SETUP,
            "monthly_price": 300.0,
            "is_recurring": False,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,
            "is_active": True,
            "is_featured": True,
            "sort_order": 10
        },
        {
            "name": "Diseño Personalizado (Mensual)",
            "code": "custom_design_monthly",
            "display_name": "Diseño Personalizado",
            "description": "Diseño personalizado continuo con actualizaciones mensuales",
            "addon_type": AddonType.SERVICE,
            "category": AddonCategory.DESIGN,
            "monthly_price": 400.0,
            "is_recurring": True,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,
            "is_active": True,
            "is_featured": False,
            "sort_order": 11
        },
        {
            "name": "Diseño Personalizado (Setup)",
            "code": "custom_design_setup",
            "display_name": "Diseño Personalizado (Setup Único)",
            "description": "Setup único de diseño personalizado ($700) + mantenimiento mensual opcional ($100/mes)",
            "addon_type": AddonType.SERVICE,
            "category": AddonCategory.DESIGN,
            "monthly_price": 700.0,
            "is_recurring": False,
            "is_quantifiable": False,
            "min_quantity": 1,
            "max_quantity": 1,
            "provides_users": 0,
            "provides_tables": 0,
            "provides_menu_items": 0,
            "enables_inventory": False,
            "enables_advanced_reports": False,
            "enables_kitchen": False,
            "available_for_plans": None,
            "is_active": True,
            "is_featured": False,
            "sort_order": 12,
            "addon_metadata": {
                "maintenance_price": 100.0,
                "maintenance_description": "Mantenimiento mensual opcional"
            }
        }
    ]
    
    print("🌱 Seeding subscription add-ons...")
    for addon_data in addons_data:
        existing = db.query(SubscriptionAddon).filter_by(code=addon_data["code"]).first()
        if existing:
            print(f"  ⏭️  Add-on '{addon_data['code']}' already exists, skipping...")
            continue
        
        addon = SubscriptionAddon(**addon_data)
        db.add(addon)
        print(f"  ✅ Created add-on: {addon_data['display_name']} (${addon_data['monthly_price']})")
    
    db.commit()
    print("✅ Subscription add-ons seeded successfully!\n")


def main():
    """Main seeding function"""
    print("\n" + "="*60)
    print("🚀 SEEDING SUBSCRIPTION PLANS AND ADD-ONS")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        seed_plans(db)
        seed_addons(db)
        
        print("="*60)
        print("✅ ALL DONE! Subscription system seeded successfully!")
        print("="*60 + "\n")
        
        # Print summary
        total_plans = db.query(SubscriptionPlan).count()
        total_addons = db.query(SubscriptionAddon).count()
        
        print(f"📊 Summary:")
        print(f"  • Total Plans: {total_plans}")
        print(f"  • Total Add-ons: {total_addons}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
