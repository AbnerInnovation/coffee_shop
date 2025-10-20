/**
 * Form validation utilities
 * 
 * This module provides reusable validation functions for forms
 * to ensure consistent validation across the application.
 */

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

/**
 * Email validation
 * Checks for valid email format with domain extension
 */
export function validateEmail(email: string): ValidationResult {
  const errors: string[] = [];
  
  if (!email) {
    errors.push('El correo electrónico es obligatorio');
    return { isValid: false, errors };
  }
  
  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    errors.push('Formato de correo electrónico inválido (ejemplo: usuario@dominio.com)');
    return { isValid: false, errors };
  }
  
  // Check for domain extension
  const domain = email.split('@')[1];
  if (domain && !domain.includes('.')) {
    errors.push('El dominio debe incluir una extensión (ejemplo: .com, .mx, .net)');
    return { isValid: false, errors };
  }
  
  return { isValid: true, errors: [] };
}

/**
 * Password validation
 * Checks for strong password requirements
 */
export function validatePassword(password: string, isRequired: boolean = true): ValidationResult {
  const errors: string[] = [];
  
  // Check if required
  if (!password) {
    if (isRequired) {
      errors.push('La contraseña es obligatoria');
    }
    return { isValid: !isRequired, errors };
  }
  
  // Length check
  if (password.length < 8) {
    errors.push('Debe tener al menos 8 caracteres');
  }
  
  // Uppercase letter check
  if (!/[A-Z]/.test(password)) {
    errors.push('Debe contener al menos una letra mayúscula');
  }
  
  // Lowercase letter check
  if (!/[a-z]/.test(password)) {
    errors.push('Debe contener al menos una letra minúscula');
  }
  
  // Digit check
  if (!/\d/.test(password)) {
    errors.push('Debe contener al menos un número');
  }
  
  // Special character check
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Debe contener al menos un carácter especial (!@#$%^&*(),.?":{}|<>)');
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Required field validation
 */
export function validateRequired(value: string | number | null | undefined, fieldName: string = 'Este campo'): ValidationResult {
  if (value === null || value === undefined || value === '') {
    return {
      isValid: false,
      errors: [`${fieldName} es obligatorio`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Minimum length validation
 */
export function validateMinLength(value: string, minLength: number, fieldName: string = 'Este campo'): ValidationResult {
  if (value.length < minLength) {
    return {
      isValid: false,
      errors: [`${fieldName} debe tener al menos ${minLength} caracteres`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Maximum length validation
 */
export function validateMaxLength(value: string, maxLength: number, fieldName: string = 'Este campo'): ValidationResult {
  if (value.length > maxLength) {
    return {
      isValid: false,
      errors: [`${fieldName} no puede tener más de ${maxLength} caracteres`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Numeric validation
 */
export function validateNumeric(value: string | number, fieldName: string = 'Este campo'): ValidationResult {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  if (isNaN(numValue)) {
    return {
      isValid: false,
      errors: [`${fieldName} debe ser un número válido`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Positive number validation
 */
export function validatePositive(value: number, fieldName: string = 'Este campo'): ValidationResult {
  if (value <= 0) {
    return {
      isValid: false,
      errors: [`${fieldName} debe ser un número positivo`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Price validation (positive number with max 2 decimals)
 */
export function validatePrice(value: number | string, fieldName: string = 'Precio'): ValidationResult {
  const errors: string[] = [];
  
  // Convert to number if string
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  
  // Check if valid number
  if (isNaN(numValue)) {
    errors.push(`${fieldName} debe ser un número válido`);
    return { isValid: false, errors };
  }
  
  // Check if positive
  if (numValue <= 0) {
    errors.push(`${fieldName} debe ser mayor a 0`);
  }
  
  // Check decimal places
  const decimalPlaces = (numValue.toString().split('.')[1] || '').length;
  if (decimalPlaces > 2) {
    errors.push(`${fieldName} no puede tener más de 2 decimales`);
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * URL validation
 */
export function validateUrl(url: string, fieldName: string = 'URL'): ValidationResult {
  if (!url) {
    return { isValid: true, errors: [] }; // URL is optional
  }
  
  try {
    new URL(url);
    return { isValid: true, errors: [] };
  } catch {
    return {
      isValid: false,
      errors: [`${fieldName} no es una URL válida`]
    };
  }
}

/**
 * Phone number validation (basic)
 */
export function validatePhone(phone: string, fieldName: string = 'Teléfono'): ValidationResult {
  if (!phone) {
    return { isValid: true, errors: [] }; // Phone is optional
  }
  
  // Remove common formatting characters
  const cleaned = phone.replace(/[\s\-\(\)\.]/g, '');
  
  // Check if contains only digits and optional + prefix
  if (!/^\+?[0-9]+$/.test(cleaned)) {
    return {
      isValid: false,
      errors: [`${fieldName} debe contener solo dígitos y opcional prefijo +`]
    };
  }
  
  // Check length (10-15 digits)
  const digitCount = cleaned.replace('+', '').length;
  if (digitCount < 10 || digitCount > 15) {
    return {
      isValid: false,
      errors: [`${fieldName} debe tener entre 10 y 15 dígitos`]
    };
  }
  
  return { isValid: true, errors: [] };
}

/**
 * Name validation (letters, spaces, hyphens, apostrophes)
 */
export function validateName(name: string, fieldName: string = 'Nombre'): ValidationResult {
  const errors: string[] = [];
  
  if (!name || !name.trim()) {
    errors.push(`${fieldName} es obligatorio`);
    return { isValid: false, errors };
  }
  
  // Allow letters (including Spanish), spaces, hyphens, apostrophes, periods
  if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-'.]+$/.test(name)) {
    errors.push(`${fieldName} contiene caracteres inválidos`);
  }
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Alphanumeric validation
 */
export function validateAlphanumeric(value: string, fieldName: string = 'Este campo'): ValidationResult {
  if (!/^[a-zA-Z0-9]+$/.test(value)) {
    return {
      isValid: false,
      errors: [`${fieldName} debe contener solo letras y números`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Range validation
 */
export function validateRange(value: number, min: number, max: number, fieldName: string = 'Este campo'): ValidationResult {
  if (value < min || value > max) {
    return {
      isValid: false,
      errors: [`${fieldName} debe estar entre ${min} y ${max}`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Date validation (not in the past)
 */
export function validateFutureDate(date: Date | string, fieldName: string = 'Fecha'): ValidationResult {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  
  if (dateObj < now) {
    return {
      isValid: false,
      errors: [`${fieldName} no puede ser una fecha pasada`]
    };
  }
  return { isValid: true, errors: [] };
}

/**
 * Combine multiple validation results
 */
export function combineValidations(...results: ValidationResult[]): ValidationResult {
  const allErrors = results.flatMap(r => r.errors);
  return {
    isValid: allErrors.length === 0,
    errors: allErrors
  };
}

/**
 * Validate entire form object
 * Returns object with field names as keys and validation results as values
 */
export function validateForm<T extends Record<string, any>>(
  formData: T,
  validationRules: Record<keyof T, (value: any) => ValidationResult>
): Record<keyof T, ValidationResult> {
  const results = {} as Record<keyof T, ValidationResult>;
  
  for (const field in validationRules) {
    results[field] = validationRules[field](formData[field]);
  }
  
  return results;
}

/**
 * Check if form has any errors
 */
export function hasFormErrors<T extends Record<string, any>>(
  validationResults: Record<keyof T, ValidationResult>
): boolean {
  return Object.values(validationResults).some(result => !result.isValid);
}

/**
 * Get all form errors as a flat array
 */
export function getFormErrors<T extends Record<string, any>>(
  validationResults: Record<keyof T, ValidationResult>
): string[] {
  return Object.values(validationResults).flatMap(result => result.errors);
}
