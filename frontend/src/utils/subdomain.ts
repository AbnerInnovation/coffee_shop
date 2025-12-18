/**
 * Utility functions for handling subdomain-based multi-restaurant routing
 */

// Cache for Electron config
let electronConfigCache: any = null;
const ELECTRON_CONFIG_KEY = 'electron_config_cache';

/**
 * Check if running in Electron
 */
export function isElectron(): boolean {
  // Check if window.electron exists (exposed by preload script)
  const hasElectronAPI = !!(window as any).electron;
  // Fallback to process check
  const hasProcess = !!(window && window.process && (window.process as any).type);
  const result = hasElectronAPI || hasProcess;
  
  console.log('[isElectron] Check:', {
    hasWindow: !!window,
    hasElectronAPI,
    hasProcess,
    processType: window && window.process ? (window.process as any).type : 'undefined',
    result
  });
  return result;
}

/**
 * Get cached Electron config from localStorage
 */
function getCachedElectronConfig(): any {
  if (!isElectron()) {
    console.log('[getCachedElectronConfig] Not Electron, returning null');
    return null;
  }
  
  try {
    const cached = localStorage.getItem(ELECTRON_CONFIG_KEY);
    console.log('[getCachedElectronConfig] Raw cached value:', cached);
    
    if (!cached) {
      console.log('[getCachedElectronConfig] No cached config found');
      return null;
    }
    
    const parsed = JSON.parse(cached);
    console.log('[getCachedElectronConfig] Parsed cache data:', parsed);
    
    // Handle both old format (direct config) and new format (with timestamp)
    if (parsed.config) {
      return parsed.config;
    }
    return parsed;
  } catch (error) {
    console.error('[getCachedElectronConfig] Error reading cache:', error);
    return null;
  }
}

/**
 * Load configuration from config.json (Electron only)
 */
async function loadElectronConfig(): Promise<any> {
  if (electronConfigCache) return electronConfigCache;
  
  try {
    // Try multiple paths for config.json
    const paths = [
      './config.json',           // Packaged app (relative to index.html)
      '/config.json',            // Dev mode
      '../config.json',          // Alternative packaged path
    ];
    
    let response: Response | null = null;
    let lastError: any = null;
    
    for (const path of paths) {
      try {
        response = await fetch(path);
        if (response.ok) {
          console.log(`[loadElectronConfig] Successfully loaded from: ${path}`);
          break;
        }
      } catch (err) {
        lastError = err;
        console.warn(`[loadElectronConfig] Failed to load from ${path}:`, err);
      }
    }
    
    if (!response || !response.ok) {
      throw lastError || new Error('Config file not found in any location');
    }
    
    electronConfigCache = await response.json();
    
    // Cache in localStorage for synchronous access
    if (isElectron()) {
      // Add timestamp to detect config changes
      const cacheData = {
        config: electronConfigCache,
        timestamp: Date.now()
      };
      localStorage.setItem(ELECTRON_CONFIG_KEY, JSON.stringify(cacheData));
    }
    
    return electronConfigCache;
  } catch (error) {
    console.error('Failed to load Electron config:', error);
    return null;
  }
}

/**
 * Extract subdomain from the current hostname
 * @returns The subdomain string or null if no subdomain
 */
export function getSubdomain(): string | null {
  // If running in Electron, use config file (check cache first)
  if (isElectron()) {
    const config = getCachedElectronConfig();
    if (config) {
      console.log('[getSubdomain] Using Electron config:', config.restaurant?.subdomain);
      return config.restaurant?.subdomain || null;
    }
  }
  
  const host = window.location.hostname;
  const parts = host.split('.');
  
  // For localhost development (e.g., restaurant1.localhost)
  if (host.includes('localhost')) {
    const subdomain = parts[0];
    return subdomain !== 'localhost' ? subdomain : null;
  }
  
  // For production (e.g., restaurant1.example.com)
  // Assumes format: subdomain.domain.tld
  if (parts.length >= 3) {
    const subdomain = parts[0];
    // Exclude 'www' as a subdomain
    return subdomain !== 'www' ? subdomain : null;
  }
  
  return null;
}

/**
 * Get the API base URL based on the current subdomain
 * @returns The full API base URL
 */
export function getApiBaseUrl(): string {
  // If running in Electron, use config file URL
  if (isElectron()) {
    const config = getCachedElectronConfig();
    if (config) {
      console.log('[getApiBaseUrl] Using Electron config:', config.restaurant?.apiUrl);
      return config.restaurant?.apiUrl || 'http://localhost:8001';
    }
  }
  
  const subdomain = getSubdomain();
  const protocol = window.location.protocol;
  
  // Check if we're in development mode
  const isDevelopment = import.meta.env.DEV;
  
  if (isDevelopment) {
    // Development: Prefer using the current base domain to retain subdomain in Host header
    const port = import.meta.env.VITE_API_PORT || '8000';
    const host = window.location.hostname; // e.g., default.shopacoffee.local
    const parts = host.split('.');
    
    // Determine base domain to use in dev
    let baseDomain = 'localhost';
    if (host.includes('localhost')) {
      baseDomain = 'localhost';
    } else if (parts.length >= 2) {
      // Use the existing base domain (e.g., shopacoffee.local)
      baseDomain = parts.slice(-2).join('.');
    }
    
    if (subdomain) {
      return `${protocol}//${subdomain}.${baseDomain}:${port}`;
    }
    return `${protocol}//${baseDomain}:${port}`;
  } else {
    // Production: Use the same host as the frontend
    return `${protocol}//${window.location.host}`;
  }
}

/**
 * Check if the current request is for a specific restaurant
 * @returns true if accessing via subdomain, false otherwise
 */
export function hasRestaurantContext(): boolean {
  return getSubdomain() !== null;
}

/**
 * Initialize Electron configuration (call this on app startup)
 * @returns Promise that resolves when config is loaded
 */
export async function initializeElectronConfig(): Promise<void> {
  console.log('[initializeElectronConfig] Starting...');
  console.log('[initializeElectronConfig] Is Electron?', isElectron());
  
  if (isElectron()) {
    const config = await loadElectronConfig();
    console.log('[initializeElectronConfig] Config loaded:', config);
    console.log('[initializeElectronConfig] Subdomain:', config?.restaurant?.subdomain);
    console.log('[initializeElectronConfig] API URL:', config?.restaurant?.apiUrl);
    
    // Verify it's in localStorage
    const cached = localStorage.getItem(ELECTRON_CONFIG_KEY);
    console.log('[initializeElectronConfig] Cached in localStorage:', cached);
  } else {
    console.log('[initializeElectronConfig] Not running in Electron, skipping config load');
  }
}

