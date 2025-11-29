/**
 * Error Translator Utility
 * 
 * Translates backend error messages (in English) using i18n.
 * Uses regex pattern matching to detect error types and extract dynamic values.
 * 
 * Best Practice: Backend sends errors in English, frontend translates them using i18n.
 */

/**
 * Translates category-related error messages
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 */
export function translateCategoryError(message: string, t: (key: string, values?: any) => string): string {
  if (!message) return '';

  // Pattern: "Cannot delete category 'NAME' because it has N menu items"
  const cannotDeleteMatch = message.match(/Cannot delete category '(.+?)' because it has (\d+) menu items?/);
  if (cannotDeleteMatch) {
    const categoryName = cannotDeleteMatch[1];
    const count = parseInt(cannotDeleteMatch[2]);
    return t('errors.category.cannot_delete_has_items', { name: categoryName, count });
  }

  // Return original message if no pattern matches
  return message;
}

/**
 * Translates menu item-related error messages
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 */
export function translateMenuItemError(message: string, t: (key: string, values?: any) => string): string {
  if (!message) return '';

  // Add patterns for menu item errors here
  // Example: "Cannot delete item 'NAME' because..."
  
  return message;
}

/**
 * Translates table-related error messages
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 */
export function translateTableError(message: string, t: (key: string, values?: any) => string): string {
  if (!message) return '';

  // Add patterns for table errors here
  // Example: "Cannot delete table 'NAME' because it has an active order"
  
  return message;
}

/**
 * Translates order-related error messages
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 */
export function translateOrderError(message: string, t: (key: string, values?: any) => string): string {
  if (!message) return '';

  // Add patterns for order errors here
  
  return message;
}

/**
 * Translates user-related error messages
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 */
export function translateUserError(message: string, t: (key: string, values?: any) => string): string {
  if (!message) return '';

  // Add patterns for user errors here
  
  return message;
}

/**
 * Translates cash register-related error messages
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 */
export function translateCashRegisterError(message: string, t: (key: string, values?: any) => string): string {
  if (!message) return '';

  // Pattern: "Cannot open a new session. There is already an open session (Session #N) for this restaurant..."
  const sessionAlreadyOpenMatch = message.match(/Cannot open a new session.*Session #(\d+)/i);
  if (sessionAlreadyOpenMatch) {
    const sessionNumber = sessionAlreadyOpenMatch[1];
    return t('errors.cash_register.session_already_open', { sessionNumber });
  }

  return message;
}

/**
 * Main error translator - attempts to translate any backend error message
 * 
 * @param message - Raw error message from backend (in English)
 * @param t - i18n translate function
 * @param context - Optional context to help determine error type
 * @returns Translated error message
 */
export function translateError(message: string, t: (key: string, values?: any) => string, context?: 'category' | 'menu' | 'table' | 'order' | 'user' | 'cash_register'): string {
  if (!message) return '';

  // Try context-specific translator first
  if (context) {
    switch (context) {
      case 'category':
        const categoryTranslation = translateCategoryError(message, t);
        if (categoryTranslation !== message) return categoryTranslation;
        break;
      case 'menu':
        const menuTranslation = translateMenuItemError(message, t);
        if (menuTranslation !== message) return menuTranslation;
        break;
      case 'table':
        const tableTranslation = translateTableError(message, t);
        if (tableTranslation !== message) return tableTranslation;
        break;
      case 'order':
        const orderTranslation = translateOrderError(message, t);
        if (orderTranslation !== message) return orderTranslation;
        break;
      case 'user':
        const userTranslation = translateUserError(message, t);
        if (userTranslation !== message) return userTranslation;
        break;
      case 'cash_register':
        const cashRegisterTranslation = translateCashRegisterError(message, t);
        if (cashRegisterTranslation !== message) return cashRegisterTranslation;
        break;
    }
  }

  // Try all translators if no context or context-specific didn't match
  const categoryTranslation = translateCategoryError(message, t);
  if (categoryTranslation !== message) return categoryTranslation;

  const menuTranslation = translateMenuItemError(message, t);
  if (menuTranslation !== message) return menuTranslation;

  const tableTranslation = translateTableError(message, t);
  if (tableTranslation !== message) return tableTranslation;

  const orderTranslation = translateOrderError(message, t);
  if (orderTranslation !== message) return orderTranslation;

  const userTranslation = translateUserError(message, t);
  if (userTranslation !== message) return userTranslation;

  const cashRegisterTranslation = translateCashRegisterError(message, t);
  if (cashRegisterTranslation !== message) return cashRegisterTranslation;

  // Return original message if no translation found
  return message;
}

/**
 * Extracts error message from different possible error object structures
 * 
 * @param err - Error object from axios/fetch
 * @returns Extracted error message string
 */
export function extractErrorMessage(err: any): string {
  return err?.response?.data?.error?.message || 
         err?.response?.data?.detail || 
         err?.response?.data?.message ||
         err?.message || 
         '';
}

/**
 * Complete error handling helper - extracts and translates error message
 * 
 * @param err - Error object from axios/fetch
 * @param t - i18n translate function
 * @param context - Optional context to help determine error type
 * @param fallback - Fallback message if extraction/translation fails
 * @returns Translated error message ready to display to user
 */
export function handleError(err: any, t: (key: string, values?: any) => string, context?: 'category' | 'menu' | 'table' | 'order' | 'user' | 'cash_register', fallback?: string): string {
  const rawMessage = extractErrorMessage(err);
  const translatedMessage = translateError(rawMessage, t, context);
  
  return translatedMessage || fallback || t('errors.generic');
}
