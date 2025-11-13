"""
Unit tests for formatting utility functions.
"""
import pytest

from app.utils.formatting import (
    format_currency,
    format_phone,
    sanitize_filename,
    truncate_string,
    slugify,
    format_percentage,
    mask_email,
    format_file_size
)


def test_format_currency():
    """Test currency formatting."""
    assert format_currency(1234.56, "USD") == "$1,234.56"
    assert format_currency(999.99, "MXN") == "$999.99"
    assert format_currency(100, "EUR") == "€100.00"


def test_format_phone_us():
    """Test US phone number formatting."""
    assert format_phone("1234567890", "US") == "(123) 456-7890"
    assert format_phone("123-456-7890", "US") == "(123) 456-7890"
    assert format_phone("(123) 456-7890", "US") == "(123) 456-7890"


def test_format_phone_mx():
    """Test Mexican phone number formatting."""
    assert format_phone("5512345678", "MX") == "55-1234-5678"


def test_sanitize_filename():
    """Test filename sanitization."""
    assert sanitize_filename("test file.txt") == "test_file.txt"
    assert sanitize_filename("test<>file.txt") == "testfile.txt"
    assert sanitize_filename("test/file.txt") == "testfile.txt"


def test_sanitize_filename_long():
    """Test sanitizing long filename."""
    long_name = "a" * 300 + ".txt"
    sanitized = sanitize_filename(long_name, max_length=255)
    
    assert len(sanitized) <= 255
    assert sanitized.endswith(".txt")


def test_truncate_string():
    """Test string truncation."""
    text = "This is a very long text that needs to be truncated"
    
    truncated = truncate_string(text, max_length=20)
    assert len(truncated) <= 20
    assert truncated.endswith("...")
    
    # Short text should not be truncated
    short = "Short"
    assert truncate_string(short, max_length=20) == "Short"


def test_slugify():
    """Test text slugification."""
    assert slugify("Hello World") == "hello-world"
    assert slugify("Test  Multiple   Spaces") == "test-multiple-spaces"
    assert slugify("Special!@#$%Characters") == "specialcharacters"
    assert slugify("  Leading and trailing  ") == "leading-and-trailing"


def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(0.15) == "15.00%"
    assert format_percentage(0.5, decimals=1) == "50.0%"
    assert format_percentage(1.0) == "100.00%"
    assert format_percentage(0.12345, decimals=3) == "12.345%"


def test_mask_email():
    """Test email masking."""
    assert mask_email("john@example.com") == "j**n@example.com"
    assert mask_email("a@example.com") == "a*@example.com"
    assert mask_email("ab@example.com") == "a*@example.com"
    assert mask_email("test.user@example.com") == "t*******r@example.com"


def test_mask_email_invalid():
    """Test masking invalid email."""
    # Should return as-is if no @ symbol
    assert mask_email("notanemail") == "notanemail"


def test_format_file_size():
    """Test file size formatting."""
    assert format_file_size(500) == "500.00 B"
    assert format_file_size(1024) == "1.00 KB"
    assert format_file_size(1024 * 1024) == "1.00 MB"
    assert format_file_size(1024 * 1024 * 1024) == "1.00 GB"
    assert format_file_size(1536) == "1.50 KB"  # 1.5 KB
