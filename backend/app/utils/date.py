"""
Date and time utility functions.
"""
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
import pytz


def get_current_utc() -> datetime:
    """
    Get current UTC datetime.
    
    Returns:
        datetime: Current UTC datetime with timezone info
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string (default: ISO-like format)
        
    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse datetime string to datetime object.
    
    Args:
        date_str: Date string to parse
        format_str: Format string to use for parsing
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If date string doesn't match format
    """
    return datetime.strptime(date_str, format_str)


def get_date_range(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    days: int = 7
) -> Tuple[datetime, datetime]:
    """
    Get a date range.
    
    If start_date and end_date are not provided, returns last N days.
    
    Args:
        start_date: Start date (optional)
        end_date: End date (optional)
        days: Number of days to go back if dates not provided
        
    Returns:
        Tuple[datetime, datetime]: (start_date, end_date)
    """
    if end_date is None:
        end_date = get_current_utc()
    
    if start_date is None:
        start_date = end_date - timedelta(days=days)
    
    return start_date, end_date


def convert_timezone(
    dt: datetime,
    from_tz: str = "UTC",
    to_tz: str = "America/Mexico_City"
) -> datetime:
    """
    Convert datetime from one timezone to another.
    
    Args:
        dt: Datetime to convert
        from_tz: Source timezone name
        to_tz: Target timezone name
        
    Returns:
        datetime: Converted datetime
    """
    if dt.tzinfo is None:
        # Assume source timezone if naive
        source_tz = pytz.timezone(from_tz)
        dt = source_tz.localize(dt)
    
    target_tz = pytz.timezone(to_tz)
    return dt.astimezone(target_tz)


def is_business_hours(
    dt: datetime,
    open_hour: int = 8,
    close_hour: int = 22
) -> bool:
    """
    Check if datetime is within business hours.
    
    Args:
        dt: Datetime to check
        open_hour: Opening hour (0-23)
        close_hour: Closing hour (0-23)
        
    Returns:
        bool: True if within business hours
    """
    return open_hour <= dt.hour < close_hour


def get_start_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get start of day (00:00:00) for given datetime.
    
    Args:
        dt: Datetime (defaults to now)
        
    Returns:
        datetime: Start of day
    """
    if dt is None:
        dt = get_current_utc()
    
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: Optional[datetime] = None) -> datetime:
    """
    Get end of day (23:59:59) for given datetime.
    
    Args:
        dt: Datetime (defaults to now)
        
    Returns:
        datetime: End of day
    """
    if dt is None:
        dt = get_current_utc()
    
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)
