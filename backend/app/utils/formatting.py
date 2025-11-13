"""
Formatting utility functions.
"""
import re
from typing import Optional
from decimal import Decimal


def format_currency(
    amount: float | Decimal,
    currency: str = "USD",
    locale: str = "en_US"
) -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, MXN, etc.)
        locale: Locale for formatting
        
    Returns:
        str: Formatted currency string
    """
    currency_symbols = {
        "USD": "$",
        "MXN": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_phone(phone: str, country_code: str = "US") -> str:
    """
    Format phone number.
    
    Args:
        phone: Phone number to format
        country_code: Country code for formatting
        
    Returns:
        str: Formatted phone number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if country_code == "US" and len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif country_code == "MX" and len(digits) == 10:
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    
    # Default: return as is
    return phone


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
        max_length: Maximum filename length
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Truncate if too long
    if len(sanitized) > max_length:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:max_length - len(ext) - 1]
        sanitized = f"{name}.{ext}" if ext else name
    
    return sanitized


def truncate_string(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        str: Slugified text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    return text.strip('-')


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage.
    
    Args:
        value: Value to format (0.15 = 15%)
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage
    """
    return f"{value * 100:.{decimals}f}%"


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    
    Args:
        email: Email to mask
        
    Returns:
        str: Masked email (e.g., j***@example.com)
    """
    if '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"
