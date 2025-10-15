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

