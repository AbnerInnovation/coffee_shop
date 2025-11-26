from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from enum import Enum

from ...db.base import get_db
from ...models.order import Order, OrderStatus, PaymentMethod
from ...models.order_item import OrderItem
from ...models.menu import MenuItem, Category
from ...models.cash_register import CashRegisterSession, SessionStatus
from ...models.restaurant import Restaurant
from ...services.user import get_current_active_user
from ...models.user import User
from ...core.dependencies import get_current_restaurant, require_admin_or_sysadmin

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)


class PeriodType(str, Enum):
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    CUSTOM = "custom"


# -----------------------------
# Top Products Report
# -----------------------------

@router.get("/top-products")
async def get_top_products(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    limit: int = Query(10, ge=1, le=50, description="Number of top products to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get top selling products with sales statistics.
    
    Returns products ordered by quantity sold, with revenue and percentage data.
    """
    try:
        # Build base query
        query = db.query(
            MenuItem.id.label('product_id'),
            MenuItem.name.label('product_name'),
            MenuItem.category_id.label('category_id'),
            func.sum(OrderItem.quantity).label('quantity_sold'),
            func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
        ).join(
            OrderItem, MenuItem.id == OrderItem.menu_item_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.is_paid == True
        )
        
        # Filter by current restaurant (from subdomain)
        query = query.filter(Order.restaurant_id == restaurant.id)
        
        # Date filtering
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            query = query.filter(Order.created_at >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Order.created_at <= end_datetime)
        
        # Category filtering
        if category_id:
            query = query.filter(MenuItem.category_id == category_id)
        
        # Group and order
        query = query.group_by(
            MenuItem.id,
            MenuItem.name,
            MenuItem.category_id
        ).order_by(
            desc('quantity_sold')
        ).limit(limit)
        
        results = query.all()
        
        # Calculate total revenue for percentage
        total_revenue = sum(r.total_revenue for r in results) if results else 0
        
        # Format response
        top_products = []
        for r in results:
            percentage = (r.total_revenue / total_revenue * 100) if total_revenue > 0 else 0
            top_products.append({
                "product_id": r.product_id,
                "product_name": r.product_name,
                "category_id": r.category_id,
                "quantity_sold": int(r.quantity_sold),
                "total_revenue": float(r.total_revenue),
                "percentage_of_sales": round(percentage, 2)
            })
        
        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_products": len(top_products),
            "total_revenue": round(total_revenue, 2),
            "top_products": top_products
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating top products report: {str(e)}")


# -----------------------------
# Dashboard Summary Report
# -----------------------------

@router.get("/dashboard")
async def get_dashboard_summary(
    period: PeriodType = Query(PeriodType.TODAY, description="Period type"),
    start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get unified dashboard with all 7 essential metrics:
    1. Total sales
    2. Number of tickets (orders)
    3. Average ticket
    4. Top products
    5. Sales by payment method
    6. Cash register summary
    7. Unavailable products
    """
    try:
        # Calculate date range based on period
        # Use UTC timezone to match database timestamps
        now = datetime.now(timezone.utc)
        
        if period == PeriodType.TODAY:
            start_datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_datetime = now
        elif period == PeriodType.WEEK:
            start_datetime = now - timedelta(days=7)
            end_datetime = now
        elif period == PeriodType.MONTH:
            start_datetime = now - timedelta(days=30)
            end_datetime = now
        elif period == PeriodType.CUSTOM:
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Custom period requires start_date and end_date")
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d").replace(hour=0, minute=0, second=0)
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        
        # Base query for orders
        # Filter by is_paid instead of status - a sale is a sale regardless of order status
        orders_query = db.query(Order).filter(
            Order.is_paid == True,
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime
        )
        
        # Filter by current restaurant (from subdomain)
        orders_query = orders_query.filter(Order.restaurant_id == restaurant.id)
        
        # 1. Total Sales & 2. Number of Tickets
        paid_orders = orders_query.all()
        total_sales = sum(order.total_amount for order in paid_orders)
        total_tickets = len(paid_orders)
        
        # 3. Average Ticket
        average_ticket = total_sales / total_tickets if total_tickets > 0 else 0
        
        # 4. Top 5 Products
        top_products_query = db.query(
            MenuItem.id,
            MenuItem.name,
            Category.name.label('category_name'),
            func.sum(OrderItem.quantity).label('quantity_sold')
        ).join(
            OrderItem, MenuItem.id == OrderItem.menu_item_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            Category, MenuItem.category_id == Category.id
        ).filter(
            Order.is_paid == True,
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime
        )
        
        # Filter by current restaurant (from subdomain)
        top_products_query = top_products_query.filter(Order.restaurant_id == restaurant.id)
        
        top_products = top_products_query.group_by(
            MenuItem.id, MenuItem.name, Category.name
        ).order_by(
            desc('quantity_sold')
        ).limit(5).all()
        
        # 5. Sales by Payment Method
        payment_breakdown = {}
        for method in PaymentMethod:
            method_orders = [o for o in paid_orders if o.payment_method == method]
            method_total = sum(o.total_amount for o in method_orders)
            payment_breakdown[method.value] = {
                "amount": round(method_total, 2),
                "percentage": round((method_total / total_sales * 100) if total_sales > 0 else 0, 2),
                "count": len(method_orders)
            }
        
        # 6. Cash Register Summary (today only)
        cash_sessions_query = db.query(CashRegisterSession).filter(
            CashRegisterSession.opened_at >= start_datetime,
            CashRegisterSession.opened_at <= end_datetime
        )
        
        # Filter by current restaurant (from subdomain)
        cash_sessions_query = cash_sessions_query.filter(
            CashRegisterSession.restaurant_id == restaurant.id
        )
        
        cash_sessions = cash_sessions_query.all()
        open_sessions = [s for s in cash_sessions if s.status == SessionStatus.OPEN]
        closed_sessions = [s for s in cash_sessions if s.status == SessionStatus.CLOSED]
        
        total_cash_collected = sum(s.final_balance or 0 for s in closed_sessions)
        
        # 7. Unavailable Products
        unavailable_query = db.query(MenuItem).filter(MenuItem.is_available == False)
        
        # Filter by current restaurant (from subdomain)
        unavailable_query = unavailable_query.filter(MenuItem.restaurant_id == restaurant.id)
        
        unavailable_products = unavailable_query.all()
        
        # Build response
        return {
            "period": {
                "type": period.value,
                "start_date": start_datetime.strftime("%Y-%m-%d"),
                "end_date": end_datetime.strftime("%Y-%m-%d"),
                "start_datetime": start_datetime.isoformat(),
                "end_datetime": end_datetime.isoformat()
            },
            "sales_summary": {
                "total_sales": round(total_sales, 2),
                "total_tickets": total_tickets,
                "average_ticket": round(average_ticket, 2)
            },
            "top_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "category_name": p.category_name,
                    "quantity_sold": int(p.quantity_sold)
                }
                for p in top_products
            ],
            "payment_breakdown": payment_breakdown,
            "cash_register": {
                "open_sessions": len(open_sessions),
                "closed_sessions": len(closed_sessions),
                "total_cash_collected": round(total_cash_collected, 2)
            },
            "inventory_alerts": {
                "unavailable_count": len(unavailable_products),
                "unavailable_products": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "category_id": p.category_id
                    }
                    for p in unavailable_products
                ]
            }
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")


# -----------------------------
# Sales Trend Report
# -----------------------------

@router.get("/sales-trend")
async def get_sales_trend(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_sysadmin),
    restaurant: Restaurant = Depends(get_current_restaurant)
):
    """
    Get daily sales trend for the specified number of days.
    Useful for charts and graphs.
    """
    try:
        # Use UTC timezone to match database timestamps
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Query orders grouped by date
        query = db.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('orders_count'),
            func.sum(Order.total_amount).label('total_sales')
        ).filter(
            Order.is_paid == True,
            Order.created_at >= start_date,
            Order.created_at <= end_date
        )
        
        # Filter by current restaurant (from subdomain)
        query = query.filter(Order.restaurant_id == restaurant.id)
        
        results = query.group_by(func.date(Order.created_at)).order_by('date').all()
        
        # Format response
        trend_data = []
        for r in results:
            trend_data.append({
                "date": r.date.strftime("%Y-%m-%d"),
                "orders_count": r.orders_count,
                "total_sales": round(float(r.total_sales), 2),
                "average_ticket": round(float(r.total_sales) / r.orders_count, 2) if r.orders_count > 0 else 0
            })
        
        return {
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days
            },
            "trend": trend_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sales trend: {str(e)}")
