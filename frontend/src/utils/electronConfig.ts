/**
 * Electron-specific configuration utilities
 * Handles restaurant configuration for desktop app
 */

const STORAGE_KEY = 'electron_restaurant_config';

export interface RestaurantConfig {
  subdomain: string;
  restaurantName: string;
  apiBaseUrl: string;
}

/**
 * Check if running in Electron
 */
export function isElectron(): boolean {
  return !!(window && window.process && (window.process as any).type);
}

/**
 * Get stored restaurant configuration
 */
export function getElectronRestaurantConfig(): RestaurantConfig | null {
  if (!isElectron()) return null;
  
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return null;
  
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

/**
 * Save restaurant configuration
 */
export function setElectronRestaurantConfig(config: RestaurantConfig): void {
  if (!isElectron()) return;
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

/**
 * Clear restaurant configuration
 */
export function clearElectronRestaurantConfig(): void {
  if (!isElectron()) return;
  
  localStorage.removeItem(STORAGE_KEY);
}

/**
 * Check if restaurant is configured
 */
export function hasElectronRestaurantConfig(): boolean {
  return getElectronRestaurantConfig() !== null;
}
