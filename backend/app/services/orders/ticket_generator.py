"""
Ticket Number Generator Service

Generates sequential ticket numbers for POS sales.
Follows Single Responsibility Principle - only handles ticket number generation.
"""

from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from app.models.order import Order
from app.core.operation_modes import OperationMode, get_mode_config


def generate_ticket_number(
    db: Session,
    restaurant_id: int,
    operation_mode: OperationMode,
    custom_date: Optional[date] = None
) -> str:
    """
    Generate a sequential ticket number based on operation mode configuration.
    
    For modes with daily tickets (POS_ONLY, CAFE_MODE, FOOD_TRUCK):
    - Format: [PREFIX]YYYYMMDD-NNN
    - Example: 20241212-001, FT-20241212-042
    
    Args:
        db: Database session
        restaurant_id: Restaurant ID
        operation_mode: Current operation mode
        custom_date: Optional custom date (defaults to today)
        
    Returns:
        Generated ticket number string
    """
    config = get_mode_config(operation_mode)
    
    # Check if this mode uses daily tickets
    if not config.get('use_daily_tickets', False):
        # For modes without daily tickets, return None (use order_number instead)
        return None
    
    # Get prefix from config
    prefix = config.get('ticket_prefix', '')
    
    # Use custom date or today
    ticket_date = custom_date or datetime.now().date()
    
    # Count tickets for this restaurant on this date
    count = db.query(Order).filter(
        Order.restaurant_id == restaurant_id,
        func.date(Order.created_at) == ticket_date,
        Order.ticket_number.isnot(None)
    ).count()
    
    # Generate ticket number
    date_str = ticket_date.strftime('%Y%m%d')
    sequence = count + 1
    
    if prefix:
        return f"{prefix}{date_str}-{sequence:03d}"
    else:
        return f"{date_str}-{sequence:03d}"


def parse_ticket_number(ticket_number: str) -> Optional[dict]:
    """
    Parse a ticket number to extract its components.
    
    Args:
        ticket_number: Ticket number string
        
    Returns:
        Dictionary with parsed components or None if invalid
        {
            'prefix': str,
            'date': date,
            'sequence': int
        }
    """
    if not ticket_number:
        return None
    
    try:
        # Split by dash to get parts
        parts = ticket_number.split('-')
        
        if len(parts) < 2:
            return None
        
        # Last part is always sequence
        sequence = int(parts[-1])
        
        # Second to last is date (YYYYMMDD)
        date_str = parts[-2]
        
        # Everything before is prefix (if any)
        prefix = '-'.join(parts[:-2]) if len(parts) > 2 else ''
        
        # Parse date
        ticket_date = datetime.strptime(date_str, '%Y%m%d').date()
        
        return {
            'prefix': prefix,
            'date': ticket_date,
            'sequence': sequence
        }
    except (ValueError, IndexError):
        return None


def get_next_ticket_number(
    db: Session,
    restaurant_id: int,
    operation_mode: OperationMode
) -> str:
    """
    Get the next ticket number for immediate use.
    This is a convenience wrapper around generate_ticket_number.
    
    Args:
        db: Database session
        restaurant_id: Restaurant ID
        operation_mode: Current operation mode
        
    Returns:
        Next ticket number
    """
    return generate_ticket_number(db, restaurant_id, operation_mode)


def validate_ticket_number_format(
    ticket_number: str,
    operation_mode: OperationMode
) -> bool:
    """
    Validate that a ticket number matches the expected format for the operation mode.
    
    Args:
        ticket_number: Ticket number to validate
        operation_mode: Operation mode to validate against
        
    Returns:
        True if valid, False otherwise
    """
    config = get_mode_config(operation_mode)
    
    # If mode doesn't use daily tickets, ticket_number should be None
    if not config.get('use_daily_tickets', False):
        return ticket_number is None
    
    # Parse and validate
    parsed = parse_ticket_number(ticket_number)
    if not parsed:
        return False
    
    # Check prefix matches
    expected_prefix = config.get('ticket_prefix', '')
    if parsed['prefix'] != expected_prefix:
        return False
    
    return True
