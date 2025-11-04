from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from ...db.base import get_db
from ...models.restaurant import Restaurant as RestaurantModel
from ...models.user import User, UserRole, User as UserModel
from ...schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantPublic, RestaurantCreationResponse
from ...schemas.user import UserCreate
from ...services.user import get_current_active_user, create_user
from ...middleware.restaurant import get_restaurant_from_request

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"]
)


def require_sysadmin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency to ensure user is a system administrator"""
    if current_user.role != UserRole.SYSADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can perform this action"
        )
    return current_user


@router.get("/current", response_model=RestaurantPublic)
async def get_current_restaurant(request: Request):
    """
    Get the current restaurant based on subdomain.
    This endpoint is public and doesn't require authentication.
    """
    restaurant = await get_restaurant_from_request(request)
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No restaurant found for this subdomain"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Restaurant with subdomain '{restaurant.subdomain}' already exists"
        )
    
    # Extract trial_days before creating restaurant
    trial_days = restaurant.trial_days if hasattr(restaurant, 'trial_days') else 14
    
    # Create new restaurant (exclude trial_days from dict)
    restaurant_data = restaurant.dict(exclude={'trial_days'})
    db_restaurant = RestaurantModel(**restaurant_data)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    
    # Automatically create trial subscription with custom trial_days
    trial_subscription = None
    try:
        from app.services.subscription_service import SubscriptionService
        subscription_service = SubscriptionService(db)
        trial_subscription = subscription_service.create_trial_subscription(db_restaurant.id, trial_days)
        print(f"✅ Trial subscription created for restaurant '{db_restaurant.name}' (ID: {db_restaurant.id})")
        print(f"   Trial duration: {trial_days} days")
        print(f"   Trial expires: {trial_subscription.trial_end_date}")
    except Exception as e:
        # Log error but don't fail restaurant creation
        print(f"⚠️ Warning: Could not create trial subscription for restaurant {db_restaurant.id}: {e}")
    
    # Automatically create admin user for the restaurant
    admin_email = ""
    admin_password = ""
    try:
        import secrets
        from app.core.security import get_password_hash
        
        admin_email = f"admin-{db_restaurant.subdomain}@shopacoffee.com"
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
    
    # Generate restaurant URL
    # TODO: Replace with actual domain from environment variable
    base_domain = "shopacoffee.local:3000"  # Development
    restaurant_url = f"http://{db_restaurant.subdomain}.{base_domain}"
    
    # Generate welcome message
    trial_expires = trial_subscription.trial_end_date if trial_subscription else None
    trial_expires_str = trial_expires.strftime("%d/%m/%Y") if trial_expires else "N/A"
    
    welcome_message = f"""
🎉 ¡Bienvenido a Cloud Restaurant!

Tu restaurante '{db_restaurant.name}' ha sido creado exitosamente.

📋 INFORMACIÓN DEL RESTAURANTE:
   • Nombre: {db_restaurant.name}
   • Subdomain: {db_restaurant.subdomain}
   • URL de acceso: {restaurant_url}

🔐 CREDENCIALES DE ADMINISTRADOR:
   • Email: {admin_email}
   • Contraseña: {admin_password}
   
   ⚠️ IMPORTANTE: Guarda esta contraseña en un lugar seguro. No se mostrará nuevamente.

🎁 PERÍODO DE PRUEBA:
   • Duración: {trial_days} días
   • Vence el: {trial_expires_str}
   • Plan incluido: Acceso completo a funcionalidades Pro

📝 PRIMEROS PASOS:

1. Accede al sistema:
   → Ingresa a: {restaurant_url}
   → Usa las credenciales proporcionadas arriba

2. Cambia tu contraseña:
   → Ve a tu perfil (icono de usuario en la esquina superior derecha)
   → Selecciona "Cambiar Contraseña"
   → Elige una contraseña segura y memorable

3. Configura tu restaurante:
   → Completa la información del restaurante (dirección, teléfono, logo)
   → Configura tu zona horaria y moneda
   → Ajusta la tasa de impuestos si aplica

4. Crea tu menú:
   → Ve a la sección "Menú"
   → Crea categorías (Bebidas, Alimentos, Postres, etc.)
   → Agrega tus productos con precios y descripciones
   → Configura ingredientes personalizables si lo necesitas

5. Configura tus mesas:
   → Ve a la sección "Mesas"
   → Crea las mesas de tu restaurante
   → Asigna números y capacidades

6. Crea usuarios adicionales:
   → Ve a la sección "Usuarios"
   → Agrega meseros, cajeros y personal de cocina
   → Asigna roles según sus responsabilidades

7. Comienza a tomar pedidos:
   → Usa la vista de "Mesas" para gestionar pedidos
   → El módulo de "Cocina" mostrará los pedidos pendientes
   → Usa "Caja" para gestionar pagos y cortes de caja

💡 CONSEJOS:
   • Explora todas las secciones para familiarizarte con el sistema
   • Revisa tu suscripción en la sección "Suscripción"
   • Antes de que expire tu prueba, elige un plan que se ajuste a tus necesidades

📞 SOPORTE:
   Si necesitas ayuda, contacta a tu administrador del sistema.

¡Éxito con tu restaurante! 🍽️
"""

    # Generate shareable message (more concise for WhatsApp/Email)
    shareable_message = f"""
🎉 ¡Tu restaurante está listo en Cloud Restaurant Admin!

🏪 Restaurante: {db_restaurant.name}
🌐 URL: {restaurant_url}

🔐 ACCESOS DE ADMINISTRADOR:
📧 Email: {admin_email}
🔑 Contraseña: {admin_password}

⚠️ IMPORTANTE: Cambia tu contraseña al iniciar sesión por primera vez.

🎁 Período de prueba: {trial_days} días (vence {trial_expires_str})

📝 PRIMEROS PASOS:
1. Ingresa con las credenciales proporcionadas
2. Cambia tu contraseña (Perfil → Cambiar Contraseña)
3. Configura la información de tu restaurante
4. Crea tu menú y categorías
5. Agrega tus mesas
6. Crea usuarios para tu personal
7. ¡Comienza a tomar pedidos!

¡Éxito! 🍽️
"""
    
    return RestaurantCreationResponse(
        restaurant=db_restaurant,
        admin_email=admin_email,
        admin_password=admin_password,
        restaurant_url=restaurant_url,
        trial_days=trial_days,
        trial_expires=trial_expires,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    db.delete(db_restaurant)
    db.commit()
