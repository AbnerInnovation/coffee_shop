from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ...db.base import get_db
from ...models.restaurant import Restaurant as RestaurantModel
from ...models.user import User, UserRole, User as UserModel
from ...models.restaurant_subscription import RestaurantSubscription, SubscriptionStatus
from ...models.order import Order, OrderStatus
from ...models.subscription_plan import SubscriptionPlan
from ...schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantPublic, RestaurantCreationResponse
from ...schemas.user import UserCreate
from ...services.user import get_current_active_user, create_user
from ...middleware.restaurant import get_restaurant_from_request
from ...core.config import settings
from ...core.exceptions import ConflictError, ForbiddenError, ResourceNotFoundError, DatabaseError
from ...core.dependencies import get_current_user_with_restaurant

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"]
)


def require_sysadmin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is a system administrator"""
    if current_user.role != UserRole.SYSADMIN:
        raise ForbiddenError("Only system administrators can perform this action", required_permission="sysadmin")
    return current_user


@router.get("/current", response_model=RestaurantPublic)
async def get_current_restaurant(request: Request):
    """
    Get the current restaurant based on subdomain.
    This endpoint is public and doesn't require authentication.
    """
    restaurant = await get_restaurant_from_request(request)
    
    if not restaurant:
        raise ResourceNotFoundError("Restaurant", "subdomain")
    
    return restaurant


@router.patch("/current", response_model=RestaurantPublic)
async def update_current_restaurant(
    updates: dict,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_restaurant)
):
    """
    Update current restaurant settings (admin only).
    Allows updating: kitchen_print_enabled, kitchen_print_paper_width, 
    customer_print_enabled, customer_print_paper_width, and allow_dine_in_without_table.
    """
    # Only admin and sysadmin can update restaurant settings
    if current_user.role not in ['admin', 'sysadmin']:
        raise ForbiddenError("Only admins can update restaurant settings")
    
    # Get restaurant from request to validate subdomain
    restaurant_from_request = await get_restaurant_from_request(request)
    
    if not restaurant_from_request:
        raise ResourceNotFoundError("Restaurant", "subdomain")
    
    # Get restaurant from db session to ensure it's persistent
    restaurant = db.query(RestaurantModel).filter(
        RestaurantModel.id == restaurant_from_request.id
    ).first()
    
    if not restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_from_request.id)
    
    # Update allowed fields
    allowed_fields = [
        'kitchen_print_enabled', 
        'kitchen_print_paper_width', 
        'customer_print_enabled', 
        'customer_print_paper_width',
        'allow_dine_in_without_table'
    ]
    for field, value in updates.items():
        if field in allowed_fields and hasattr(restaurant, field):
            setattr(restaurant, field, value)
    
    db.commit()
    db.refresh(restaurant)
    
    return restaurant


@router.get("/", response_model=List[Restaurant])
async def list_restaurants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    List all restaurants (sysadmin only).
    """
    restaurants = db.query(RestaurantModel).offset(skip).limit(limit).all()
    return restaurants


@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Get a specific restaurant by ID (sysadmin only).
    """
    restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_id)
    
    return restaurant


@router.post("/", response_model=RestaurantCreationResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Create a new restaurant (sysadmin only).
    Automatically creates:
    1. A trial subscription (14, 30, or 60 days)
    2. An admin user with email: admin-{subdomain}@shopacoffee.com
    Returns a complete welcome message with access credentials.
    """
    # Check if subdomain already exists
    existing = db.query(RestaurantModel).filter(
        RestaurantModel.subdomain == restaurant.subdomain
    ).first()
    
    if existing:
        raise ConflictError(
            f"Restaurant with subdomain '{restaurant.subdomain}' already exists",
            resource="Restaurant"
        )
    
    # Extract trial_days, admin_email, plan_id, and business_type before creating restaurant
    trial_days = restaurant.trial_days if hasattr(restaurant, 'trial_days') else 14
    custom_admin_email = restaurant.admin_email if hasattr(restaurant, 'admin_email') else None
    plan_id = restaurant.plan_id if hasattr(restaurant, 'plan_id') else None
    business_type = restaurant.business_type if hasattr(restaurant, 'business_type') else 'restaurant'
    
    # Debug log
    print(f"🔍 Restaurant creation request:")
    print(f"   Name: {restaurant.name}")
    print(f"   Subdomain: {restaurant.subdomain}")
    print(f"   Business Type: {business_type}")
    print(f"   Plan ID: {plan_id if plan_id else '(trial)'}")
    print(f"   Trial days: {trial_days}")
    print(f"   Custom admin email: {custom_admin_email if custom_admin_email else '(not provided)'}")
    
    # Create new restaurant (exclude trial_days, admin_email, and plan_id from dict - they're not DB fields)
    restaurant_data = restaurant.dict(exclude={'trial_days', 'admin_email', 'plan_id'})
    print(f"📦 Restaurant data to create: {restaurant_data}")
    print(f"   business_type in data: {restaurant_data.get('business_type', 'NOT FOUND')}")
    db_restaurant = RestaurantModel(**restaurant_data)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    print(f"✅ Restaurant created with business_type: {db_restaurant.business_type}")
    
    # Create subscription based on plan_id
    trial_subscription = None
    try:
        if plan_id:
            # Create paid subscription with selected plan
            from app.services.subscription import create_paid_subscription
            trial_subscription = create_paid_subscription(
                db=db,
                restaurant_id=db_restaurant.id,
                plan_id=plan_id,
                billing_cycle='monthly'
            )
            print(f"✅ Paid subscription created for restaurant '{db_restaurant.name}' (ID: {db_restaurant.id})")
            print(f"   Plan ID: {plan_id}")
        else:
            # Create trial subscription with custom trial_days
            from app.services.subscription import create_trial_subscription
            trial_subscription = create_trial_subscription(db, db_restaurant.id, trial_days)
            print(f"✅ Trial subscription created for restaurant '{db_restaurant.name}' (ID: {db_restaurant.id})")
            print(f"   Trial duration: {trial_days} days")
            print(f"   Trial expires: {trial_subscription.trial_end_date}")
    except Exception as e:
        # Log error but don't fail restaurant creation
        print(f"⚠️ Warning: Could not create subscription for restaurant {db_restaurant.id}: {e}")
    
    # Automatically create admin user for the restaurant
    admin_email = ""
    admin_password = ""
    try:
        import secrets
        from app.core.security import get_password_hash
        
        # Use custom admin email if provided, otherwise use default pattern
        if custom_admin_email:
            admin_email = custom_admin_email
            print(f"📧 Using custom admin email: {admin_email}")
        else:
            admin_email = f"admin-{db_restaurant.subdomain}@shopacoffee.com"
            print(f"📧 Using default admin email: {admin_email}")
        
        admin_password = secrets.token_urlsafe(16)  # Generate secure random password
        
        # Check if admin user already exists
        from app.services.user import get_user_by_email
        existing_admin = get_user_by_email(db, email=admin_email)
        
        if not existing_admin:
            admin_user = UserModel(
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                full_name=f"Admin {db_restaurant.name}",
                role=UserRole.ADMIN,
                is_active=True,
                restaurant_id=db_restaurant.id
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print(f"✅ Admin user created for restaurant '{db_restaurant.name}'")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   ⚠️  IMPORTANT: Save this password! It won't be shown again.")
        else:
            print(f"⚠️ Admin user already exists: {admin_email}")
            
    except Exception as e:
        # Log error but don't fail restaurant creation
        print(f"⚠️ Warning: Could not create admin user for restaurant {db_restaurant.id}: {e}")
    
    # Generate restaurant URL from environment variables
    restaurant_url = f"{settings.BASE_PROTOCOL}://{db_restaurant.subdomain}.{settings.BASE_DOMAIN}"
    
    # Get business type from the created restaurant (use db value, not request value)
    actual_business_type = db_restaurant.business_type
    print(f"🔍 Using business_type from db_restaurant: {actual_business_type}")
    
    # Business type labels and customization
    business_labels = {
        'restaurant': {'name': 'restaurante', 'emoji': '🍽️'},
        'cafe': {'name': 'cafetería', 'emoji': '☕'},
        'food_truck': {'name': 'food truck', 'emoji': '🚚'},
        'churreria': {'name': 'churrería', 'emoji': '🥨'},
        'bakery': {'name': 'panadería', 'emoji': '🥖'},
        'bar': {'name': 'bar', 'emoji': '🍺'},
        'fast_food': {'name': 'comida rápida', 'emoji': '🍔'},
        'other': {'name': 'negocio', 'emoji': '🏪'}
    }
    
    business_info = business_labels.get(actual_business_type, business_labels['other'])
    business_name = business_info['name']
    business_emoji = business_info['emoji']
    
    print(f"📊 Business type for messages: {actual_business_type} -> {business_name} {business_emoji}")
    
    # Customize steps based on business type
    # Businesses that don't typically use tables
    no_table_businesses = ['food_truck', 'churreria', 'bakery', 'fast_food']
    uses_tables = actual_business_type not in no_table_businesses
    
    if uses_tables:
        steps = """📝 PRIMEROS PASOS:
1. Ingresa al sistema con las credenciales proporcionadas
2. Cambia tu contraseña
3. Configura la información de tu negocio
4. Crea tu menú y categorías
5. Agrega tus mesas
6. Crea usuarios para tu personal
7. ¡Comienza a tomar pedidos!"""
    else:
        steps = """📝 PRIMEROS PASOS:
1. Ingresa al sistema con las credenciales proporcionadas
2. Cambia tu contraseña
3. Configura la información de tu negocio
4. Crea tu menú y categorías de productos
5. Crea usuarios para tu personal (cajeros, cocina)
6. ¡Comienza a vender usando el POS!"""
    
    # Determine subscription info
    subscription_info = ""
    subscription_plan_name = None
    trial_expires = None
    tips_section = ""
    
    if plan_id:
        # Paid subscription
        from app.services.subscription import get_plan_by_id
        plan = get_plan_by_id(db, plan_id)
        subscription_plan_name = plan.display_name
        subscription_info = f"""💳 SUSCRIPCIÓN ACTIVA:
• Plan: {plan.display_name}
• Precio: ${plan.monthly_price:.2f}/mes
• Estado: Activo
• Acceso completo a todas las funcionalidades del plan"""
        tips_section = """💡 CONSEJOS:
• Explora todas las secciones para familiarizarte con el sistema
• Revisa tu suscripción en la sección "Suscripción"
• Gestiona tu facturación y pagos desde el panel de suscripción"""
    else:
        # Trial subscription
        trial_expires = trial_subscription.trial_end_date if trial_subscription else None
        trial_expires_str = trial_expires.strftime("%d/%m/%Y") if trial_expires else "N/A"
        subscription_info = f"""🎁 PERÍODO DE PRUEBA:
• Duración: {trial_days} días
• Vence el: {trial_expires_str}
• Acceso completo a funcionalidades Pro"""
        tips_section = """💡 CONSEJOS:
• Explora todas las secciones para familiarizarte con el sistema
• Revisa tu suscripción en la sección "Suscripción"
• Antes de que expire tu prueba, elige un plan que se ajuste a tus necesidades"""
    
    welcome_message = f"""
🎉 ¡Bienvenido a Cloud Restaurant!

Tu {business_name} "{db_restaurant.name}" ha sido creado exitosamente.

📋 ACCESO AL SISTEMA:
🌐 URL: {restaurant_url}
📧 Email: {admin_email}
🔑 Contraseña: {admin_password}

⚠️ IMPORTANTE: 
• Cambia tu contraseña al iniciar sesión por primera vez
• Ve a tu perfil → Cambiar Contraseña

{subscription_info}

{steps}

{tips_section}

¡Éxito con tu {business_name}! {business_emoji}
"""

    # Generate shareable message (more concise for WhatsApp/Email)
    if plan_id:
        shareable_subscription_info = f"💳 Plan: {subscription_plan_name}"
    else:
        trial_expires_str = trial_expires.strftime("%d/%m/%Y") if trial_expires else "N/A"
        shareable_subscription_info = f"🎁 Período de prueba: {trial_days} días (vence {trial_expires_str})"
    
    # Use personalized steps for shareable message too
    if uses_tables:
        shareable_steps = """📝 PRIMEROS PASOS:
1. Ingresa con las credenciales proporcionadas
2. Cambia tu contraseña (Perfil → Cambiar Contraseña)
3. Configura la información de tu negocio
4. Crea tu menú y categorías
5. Agrega tus mesas
6. Crea usuarios para tu personal
7. ¡Comienza a tomar pedidos!"""
    else:
        shareable_steps = """📝 PRIMEROS PASOS:
1. Ingresa con las credenciales proporcionadas
2. Cambia tu contraseña (Perfil → Cambiar Contraseña)
3. Configura la información de tu negocio
4. Crea tu menú y categorías de productos
5. Crea usuarios para tu personal (cajeros, cocina)
6. ¡Comienza a vender usando el POS!"""
    
    shareable_message = f"""
🎉 ¡Tu {business_name} está listo en Cloud Restaurant Admin!

🏪 {db_restaurant.name}
🌐 URL: {restaurant_url}

🔐 ACCESOS DE ADMINISTRADOR:
📧 Email: {admin_email}
🔑 Contraseña: {admin_password}

⚠️ IMPORTANTE: Cambia tu contraseña al iniciar sesión por primera vez.

{shareable_subscription_info}

{shareable_steps}

¡Éxito! {business_emoji}
"""
    
    return RestaurantCreationResponse(
        restaurant=db_restaurant,
        admin_email=admin_email,
        admin_password=admin_password,
        restaurant_url=restaurant_url,
        trial_days=trial_days if not plan_id else None,
        trial_expires=trial_expires,
        subscription_plan=subscription_plan_name,
        welcome_message=welcome_message,
        shareable_message=shareable_message
    )


@router.put("/{restaurant_id}", response_model=Restaurant)
async def update_restaurant(
    restaurant_id: int,
    restaurant: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Update a restaurant (sysadmin only).
    """
    db_restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not db_restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_id)
    
    # Update fields
    update_data = restaurant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_restaurant, field, value)
    
    db.commit()
    db.refresh(db_restaurant)
    
    return db_restaurant


@router.get("/{restaurant_id}/admins")
async def get_restaurant_admins(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Get all admin users for a specific restaurant (sysadmin only).
    """
    # Verify restaurant exists
    db_restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not db_restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_id)
    
    # Get all admin users for this restaurant
    admins = db.query(UserModel).filter(
        UserModel.restaurant_id == restaurant_id,
        UserModel.role == UserRole.ADMIN,
        UserModel.deleted_at == None
    ).all()
    
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": db_restaurant.name,
        "admins": [
            {
                "id": admin.id,
                "email": admin.email,
                "full_name": admin.full_name,
                "created_at": admin.created_at.isoformat() if admin.created_at else None
            }
            for admin in admins
        ]
    }


@router.post("/{restaurant_id}/admin")
async def create_restaurant_admin(
    restaurant_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Create an admin user for a specific restaurant (sysadmin only).
    """
    # Verify restaurant exists
    db_restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not db_restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_id)
    
    # Force role to be admin
    user_data.role = UserRole.ADMIN
    user_data.restaurant_id = restaurant_id
    
    # Create the admin user
    try:
        new_admin = create_user(db, user_data)
        return {
            "message": f"Admin user created successfully for {db_restaurant.name}",
            "user": {
                "id": new_admin.id,
                "email": new_admin.email,
                "full_name": new_admin.full_name,
                "role": new_admin.role,
                "restaurant_id": new_admin.restaurant_id
            }
        }
    except Exception as e:
        raise DatabaseError(f"Failed to create admin user: {str(e)}", operation="create")


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Delete a restaurant (sysadmin only).
    Warning: This will cascade delete all related data!
    """
    db_restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    
    if not db_restaurant:
        raise ResourceNotFoundError("Restaurant", restaurant_id)
    
    db.delete(db_restaurant)
    db.commit()


@router.get("/stats/global", response_model=Dict[str, Any])
async def get_global_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sysadmin)
):
    """
    Get global system statistics (sysadmin only).
    Returns overview of all restaurants, subscriptions, users, and revenue.
    """
    # Total restaurants
    total_restaurants = db.query(func.count(RestaurantModel.id)).scalar()
    
    # Active restaurants (with active subscription)
    active_restaurants = db.query(func.count(func.distinct(RestaurantModel.id))).join(
        RestaurantSubscription,
        RestaurantModel.id == RestaurantSubscription.restaurant_id
    ).filter(
        RestaurantSubscription.status == SubscriptionStatus.ACTIVE
    ).scalar()
    
    # Trial restaurants
    trial_restaurants = db.query(func.count(func.distinct(RestaurantModel.id))).join(
        RestaurantSubscription,
        RestaurantModel.id == RestaurantSubscription.restaurant_id
    ).filter(
        RestaurantSubscription.status == SubscriptionStatus.TRIAL
    ).scalar()
    
    # Expired/Cancelled restaurants (suspended)
    suspended_restaurants = db.query(func.count(func.distinct(RestaurantModel.id))).join(
        RestaurantSubscription,
        RestaurantModel.id == RestaurantSubscription.restaurant_id
    ).filter(
        RestaurantSubscription.status.in_([SubscriptionStatus.EXPIRED, SubscriptionStatus.CANCELLED])
    ).scalar()
    
    # Total users by role
    total_users = db.query(func.count(UserModel.id)).scalar()
    admin_users = db.query(func.count(UserModel.id)).filter(UserModel.role == UserRole.ADMIN).scalar()
    staff_users = db.query(func.count(UserModel.id)).filter(UserModel.role == UserRole.STAFF).scalar()
    
    # Monthly Recurring Revenue (MRR)
    # Sum total_price for monthly subscriptions, or total_price/12 for annual
    mrr_monthly = db.query(func.sum(RestaurantSubscription.total_price)).filter(
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]),
        RestaurantSubscription.billing_cycle == 'monthly'
    ).scalar() or 0
    
    mrr_annual = db.query(func.sum(RestaurantSubscription.total_price)).filter(
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]),
        RestaurantSubscription.billing_cycle == 'annual'
    ).scalar() or 0
    
    # Convert annual to monthly (divide by 12)
    mrr = mrr_monthly + (mrr_annual / 12)
    
    # Pending payments (subscriptions expiring in next 7 days)
    next_week = datetime.utcnow() + timedelta(days=7)
    pending_payments = db.query(func.count(RestaurantSubscription.id)).filter(
        RestaurantSubscription.current_period_end <= next_week,
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
    ).scalar()
    
    # Recent activity (restaurants created in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_restaurants_30d = db.query(func.count(RestaurantModel.id)).filter(
        RestaurantModel.created_at >= thirty_days_ago
    ).scalar()
    
    # Total orders across all restaurants (last 30 days)
    total_orders_30d = db.query(func.count(Order.id)).filter(
        Order.created_at >= thirty_days_ago
    ).scalar()
    
    # Revenue from completed orders (last 30 days)
    revenue_30d = db.query(func.sum(Order.total_amount)).filter(
        Order.created_at >= thirty_days_ago,
        Order.status == OrderStatus.COMPLETED
    ).scalar() or 0
    
    # Subscription distribution by plan
    subscription_distribution = db.query(
        SubscriptionPlan.name,
        func.count(RestaurantSubscription.id).label('count')
    ).join(
        RestaurantSubscription,
        SubscriptionPlan.id == RestaurantSubscription.plan_id
    ).filter(
        RestaurantSubscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
    ).group_by(SubscriptionPlan.name).all()
    
    plan_distribution = {plan: count for plan, count in subscription_distribution}
    
    return {
        "restaurants": {
            "total": total_restaurants,
            "active": active_restaurants,
            "trial": trial_restaurants,
            "suspended": suspended_restaurants,
            "new_last_30_days": new_restaurants_30d
        },
        "users": {
            "total": total_users,
            "admins": admin_users,
            "staff": staff_users
        },
        "revenue": {
            "mrr": float(mrr),
            "revenue_30d": float(revenue_30d),
            "pending_payments": pending_payments
        },
        "activity": {
            "orders_30d": total_orders_30d
        },
        "subscription_distribution": plan_distribution
    }
