/**
 * Utility functions for handling subdomain-based multi-restaurant routing
 */

/**
 * Extract subdomain from the current hostname
 * @returns The subdomain string or null if no subdomain
 */
export function getSubdomain(): string | null {
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
 * Redirect to a specific restaurant subdomain
 * @param subdomain The restaurant subdomain to redirect to
 */
export function redirectToRestaurant(subdomain: string): void {
  const protocol = window.location.protocol;
  const host = window.location.hostname;
  const port = window.location.port;
  
  // Determine the base domain
  let baseDomain: string;
  
  if (host.includes('localhost')) {
    baseDomain = 'localhost';
  } else {
    // Extract domain.tld from current host
    const parts = host.split('.');
    baseDomain = parts.length >= 2 ? parts.slice(-2).join('.') : host;
  }
  
  // Build new URL
  const portSuffix = port ? `:${port}` : '';
  const newUrl = `${protocol}//${subdomain}.${baseDomain}${portSuffix}${window.location.pathname}`;
  
  window.location.href = newUrl;
}

/**
 * Get the restaurant-aware frontend URL
 * @param path Optional path to append
 * @returns Full URL with subdomain
 */
export function getRestaurantUrl(path: string = ''): string {
  const subdomain = getSubdomain();
  const protocol = window.location.protocol;
  const host = window.location.hostname;
  const port = window.location.port;
  
  const portSuffix = port ? `:${port}` : '';
  
  if (subdomain) {
    return `${protocol}//${subdomain}.${host}${portSuffix}${path}`;
  }
  
  return `${protocol}//${host}${portSuffix}${path}`;
}
