import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

/**
 * Format date to locale date string
 * @param date - Date string, Date object, or null/undefined
 * @returns Formatted date string or 'N/A' if invalid
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return 'N/A';
  try {
    return new Date(date).toLocaleDateString('es-ES');
  } catch {
    return 'N/A';
  }
}

/**
 * Format date with custom options
 * @param date - Date string, Date object, or null/undefined
 * @param options - Intl.DateTimeFormatOptions
 * @returns Formatted date string or 'N/A' if invalid
 */
export function formatDateWithOptions(
  date: string | Date | null | undefined,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }
): string {
  if (!date) return 'N/A';
  try {
    return new Date(date).toLocaleDateString('es-ES', options);
  } catch {
    return 'N/A';
  }
}

/**
 * Format date and time to locale string
 * @param date - Date string, Date object, or null/undefined
 * @returns Formatted date and time string or 'N/A' if invalid
 */
export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return 'N/A';
  try {
    return new Date(date).toLocaleString('es-ES');
  } catch {
    return 'N/A';
  }
}

/**
 * Format time only (HH:MM)
 * @param date - Date string or Date object
 * @returns Formatted time string (HH:MM)
 */
export function formatTime(date: string | Date): string {
  return new Date(date).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

/**
 * Format time ago (e.g., "hace 5 minutos")
 * @param date - Date string, Date object, or null/undefined
 * @returns Formatted relative time string or empty string if invalid
 */
export function formatTimeAgo(date: string | Date | null | undefined): string {
  if (!date) return '';
  try {
    return formatDistanceToNow(new Date(date), { 
      addSuffix: true,
      locale: es
    });
  } catch {
    return '';
  }
}

/**
 * Format date and time with short time format
 * @param date - Date string or null/undefined
 * @returns Formatted date and time string
 */
export function formatDateTimeShort(date: string | null | undefined): string {
  if (!date) return 'N/A';
  try {
    const d = new Date(date);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  } catch {
    return 'N/A';
  }
}
