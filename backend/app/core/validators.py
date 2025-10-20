"""
Reusable validation and sanitization utilities for Pydantic schemas.

This module provides common validation functions to reduce code duplication
across schema files and ensure consistent validation behavior.
"""

import re
from typing import Optional


def sanitize_text(value: Optional[str]) -> Optional[str]:
    """
    Remove potentially dangerous characters from text input.
    
    - Removes HTML tags
    - Removes < and > characters
    - Strips leading/trailing whitespace
    
    Args:
        value: Input string to sanitize
        
    Returns:
        Sanitized string or None if input was None
    """
    if value:
        # Remove HTML tags
        value = re.sub(r'<[^>]*>', '', value)
        # Remove remaining < and > characters
        value = re.sub(r'[<>]', '', value)
        return value.strip()
    return value


def validate_alphanumeric_with_spaces(
    value: Optional[str], 
    field_name: str = "Field",
    allow_hyphen: bool = True,
    allow_period: bool = True
) -> Optional[str]:
    """
    Validate that a string contains only alphanumeric characters, spaces, and optionally hyphens/periods.
    
    Args:
        value: Input string to validate
        field_name: Name of the field (for error messages)
        allow_hyphen: Whether to allow hyphen characters
        allow_period: Whether to allow period characters
        
    Returns:
        Sanitized and validated string
        
    Raises:
        ValueError: If string contains invalid characters
    """
    if value:
        # First sanitize
        value = sanitize_text(value)
        
        # Build pattern based on allowed characters
        pattern = r'^[a-zA-Z0-9\s'
        if allow_hyphen:
            pattern += r'\-'
        if allow_period:
            pattern += r'\.'
        pattern += r']+$'
        
        if not re.match(pattern, value):
            raise ValueError(f'{field_name} contiene caracteres inválidos')
    
    return value


def validate_name(value: Optional[str], field_name: str = "Name") -> Optional[str]:
    """
    Validate and sanitize a person's name.
    
    Allows: letters (including Spanish characters), spaces, hyphens, apostrophes, periods
    
    Args:
        value: Input name to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Sanitized and validated name
        
    Raises:
        ValueError: If name contains invalid characters or is empty
    """
    if value:
        # First sanitize
        value = sanitize_text(value)
        
        # Allow letters (including Spanish), spaces, hyphens, apostrophes, periods
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'.]+$', value):
            raise ValueError(f'{field_name} contiene caracteres inválidos')
        
        # Ensure not just whitespace
        if not value.strip():
            raise ValueError(f'{field_name} no puede estar vacío')
    
    return value


def validate_url(value: Optional[str], field_name: str = "URL") -> Optional[str]:
    """
    Validate URL format.
    
    Ensures URL starts with http:// or https://
    
    Args:
        value: Input URL to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Sanitized and validated URL
        
    Raises:
        ValueError: If URL format is invalid
    """
    if value:
        # Remove dangerous characters
        value = re.sub(r'[<>]', '', value)
        
        # Check URL format
        if not re.match(r'^https?://', value):
            raise ValueError(f'{field_name} debe comenzar con http:// o https://')
        
        return value.strip()
    return value


def validate_email(value: Optional[str], field_name: str = "Email") -> Optional[str]:
    """
    Validate email format.
    
    Basic validation: must contain @ and domain with .
    
    Args:
        value: Input email to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Sanitized and validated email
        
    Raises:
        ValueError: If email format is invalid
    """
    if value:
        # Remove dangerous characters
        value = re.sub(r'[<>]', '', value)
        
        # Basic email validation
        if '@' not in value or '.' not in value.split('@')[1]:
            raise ValueError(f'Formato de {field_name.lower()} inválido')
        
        return value.strip()
    return value


def validate_phone(value: Optional[str], field_name: str = "Phone") -> Optional[str]:
    """
    Validate phone number format.
    
    Allows: digits, optional + prefix, common formatting characters (spaces, hyphens, parentheses, periods)
    Requires: 10-15 digits
    
    Args:
        value: Input phone number to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Original formatted phone number (if valid)
        
    Raises:
        ValueError: If phone format is invalid
    """
    if value:
        # Remove common formatting characters for validation
        cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
        
        # Check if it contains only digits and optional + prefix
        if not re.match(r'^\+?[0-9]+$', cleaned):
            raise ValueError(f'{field_name} debe contener solo dígitos y prefijo + opcional')
        
        # Check length (10-15 digits)
        digit_count = len(cleaned.replace('+', ''))
        if digit_count < 10 or digit_count > 15:
            raise ValueError(f'{field_name} debe tener entre 10 y 15 dígitos')
        
        return value
    return value


def validate_currency_code(value: Optional[str], field_name: str = "Currency") -> Optional[str]:
    """
    Validate and normalize currency code.
    
    Ensures 3-letter ISO 4217 currency code (e.g., USD, EUR, MXN)
    
    Args:
        value: Input currency code to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Uppercase 3-letter currency code
        
    Raises:
        ValueError: If currency code format is invalid
    """
    if value:
        # Normalize to uppercase
        value = value.upper()
        
        # Validate 3-letter code
        if not re.match(r'^[A-Z]{3}$', value):
            raise ValueError(f'{field_name} debe ser un código ISO de 3 letras (ej: USD, EUR, MXN)')
        
        return value
    return value


def validate_subdomain(value: str, field_name: str = "Subdomain") -> str:
    """
    Validate subdomain format.
    
    Allows: lowercase letters, numbers, hyphens
    Restrictions: no leading/trailing hyphens, minimum 3 characters
    
    Args:
        value: Input subdomain to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Validated subdomain
        
    Raises:
        ValueError: If subdomain format is invalid
    """
    if not re.match(r'^[a-z0-9-]+$', value):
        raise ValueError(f'{field_name} debe contener solo letras minúsculas, números y guiones')
    
    if value.startswith('-') or value.endswith('-'):
        raise ValueError(f'{field_name} no puede comenzar o terminar con un guion')
    
    if len(value) < 3:
        raise ValueError(f'{field_name} debe tener al menos 3 caracteres')
    
    return value


def validate_password_strength(value: str, field_name: str = "Password") -> str:
    """
    Validate password strength.
    
    Requirements:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        value: Input password to validate
        field_name: Name of the field (for error messages)
        
    Returns:
        Validated password
        
    Raises:
        ValueError: If password doesn't meet strength requirements
    """
    if not re.search(r'[A-Z]', value):
        raise ValueError(f'{field_name} debe contener al menos una letra mayúscula')
    
    if not re.search(r'[a-z]', value):
        raise ValueError(f'{field_name} debe contener al menos una letra minúscula')
    
    if not re.search(r'\d', value):
        raise ValueError(f'{field_name} debe contener al menos un dígito')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValueError(f'{field_name} debe contener al menos un carácter especial')
    
    return value


def validate_discount_price(discount: Optional[float], regular_price: float) -> Optional[float]:
    """
    Validate that discount price is less than regular price.
    
    Args:
        discount: Discount price
        regular_price: Regular price
        
    Returns:
        Validated discount price
        
    Raises:
        ValueError: If discount price is >= regular price
    """
    if discount is not None and discount >= regular_price:
        raise ValueError('El precio de descuento debe ser menor que el precio regular')
    
    return discount
