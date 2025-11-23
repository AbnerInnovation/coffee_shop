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

/**
 * Calculate difference in days between two dates
 * @param targetDateStr - Target date string (YYYY-MM-DD)
 * @param startDate - Start date (defaults to today)
 * @returns Number of days difference (minimum 1)
 */
export function calculateDaysDifference(
  targetDateStr: string, 
  startDate: Date = new Date()
): number {
  if (!targetDateStr) return 14;
  
  const start = new Date(startDate);
  start.setHours(0, 0, 0, 0);
  
  const end = new Date(targetDateStr);
  end.setHours(0, 0, 0, 0);
  
  // Check if dates are valid
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return 14;
  }
  
  const diffTime = end.getTime() - start.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays > 0 ? diffDays : 1;
}

/**
 * Get tomorrow's date in YYYY-MM-DD format
 * @param fromDate - Optional starting date (defaults to today)
 * @returns Date string
 */
export function getTomorrowDateString(fromDate: Date = new Date()): string {
  const tomorrow = new Date(fromDate);
  tomorrow.setDate(tomorrow.getDate() + 1);
  return tomorrow.toISOString().split('T')[0];
}
