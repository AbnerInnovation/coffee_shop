/**
 * Global in-memory token cache for Safari compatibility
 * Safari sometimes blocks localStorage access during navigation
 */

let _cachedToken: string | null = null;

export function setGlobalToken(token: string | null) {
  _cachedToken = token;
  console.log('🔐 Global token set:', !!token);
}

export function getGlobalToken(): string | null {
  return _cachedToken;
}
