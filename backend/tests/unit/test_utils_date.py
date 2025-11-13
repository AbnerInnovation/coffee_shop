"""
Unit tests for date utility functions.
"""
import pytest
from datetime import datetime, timedelta, timezone

from app.utils.date import (
    get_current_utc,
    format_datetime,
    parse_datetime,
    get_date_range,
    get_start_of_day,
    get_end_of_day,
    is_business_hours
)


def test_get_current_utc():
    """Test getting current UTC datetime."""
    now = get_current_utc()
    
    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.tzinfo == timezone.utc


def test_format_datetime():
    """Test datetime formatting."""
    dt = datetime(2024, 1, 15, 14, 30, 45)
    
    # Default format
    formatted = format_datetime(dt)
    assert formatted == "2024-01-15 14:30:45"
    
    # Custom format
    formatted = format_datetime(dt, "%Y/%m/%d")
    assert formatted == "2024/01/15"


def test_parse_datetime():
    """Test datetime parsing."""
    date_str = "2024-01-15 14:30:45"
    
    dt = parse_datetime(date_str)
    assert isinstance(dt, datetime)
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15
    assert dt.hour == 14
    assert dt.minute == 30


def test_parse_datetime_invalid():
    """Test parsing invalid datetime string."""
    with pytest.raises(ValueError):
        parse_datetime("invalid-date")


def test_get_date_range_default():
    """Test getting default date range (last 7 days)."""
    start, end = get_date_range()
    
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert start < end
    
    # Should be approximately 7 days apart
    delta = end - start
    assert 6 <= delta.days <= 8


def test_get_date_range_custom():
    """Test getting custom date range."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    start, end = get_date_range(start_date, end_date)
    
    assert start == start_date
    assert end == end_date


def test_get_start_of_day():
    """Test getting start of day."""
    dt = datetime(2024, 1, 15, 14, 30, 45, 123456)
    
    start = get_start_of_day(dt)
    
    assert start.year == 2024
    assert start.month == 1
    assert start.day == 15
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0
    assert start.microsecond == 0


def test_get_end_of_day():
    """Test getting end of day."""
    dt = datetime(2024, 1, 15, 14, 30, 45)
    
    end = get_end_of_day(dt)
    
    assert end.year == 2024
    assert end.month == 1
    assert end.day == 15
    assert end.hour == 23
    assert end.minute == 59
    assert end.second == 59


def test_is_business_hours():
    """Test business hours check."""
    # During business hours (10 AM)
    dt_business = datetime(2024, 1, 15, 10, 0, 0)
    assert is_business_hours(dt_business) is True
    
    # Before business hours (6 AM)
    dt_before = datetime(2024, 1, 15, 6, 0, 0)
    assert is_business_hours(dt_before) is False
    
    # After business hours (11 PM)
    dt_after = datetime(2024, 1, 15, 23, 0, 0)
    assert is_business_hours(dt_after) is False


def test_is_business_hours_custom():
    """Test business hours check with custom hours."""
    dt = datetime(2024, 1, 15, 9, 0, 0)
    
    # 9 AM is within 8-22
    assert is_business_hours(dt, open_hour=8, close_hour=22) is True
    
    # 9 AM is before 10-20
    assert is_business_hours(dt, open_hour=10, close_hour=20) is False
