/**
 * Storage utility with fallback for iOS/Safari restrictions
 * 
 * Safari (especially iOS) has strict privacy settings that can block localStorage:
 * - Private browsing mode
 * - "Prevent Cross-Site Tracking" enabled
 * - Third-party cookies blocked
 * 
 * This utility provides a memory fallback when localStorage is unavailable.
 */

// In-memory fallback storage
const memoryStorage: Record<string, string> = {};

// Check if localStorage is available and working
function isLocalStorageAvailable(): boolean {
  try {
    const testKey = '__storage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch (e) {
    console.warn('localStorage is not available, using memory fallback:', e);
    return false;
  }
}

// Check if sessionStorage is available and working
function isSessionStorageAvailable(): boolean {
  try {
    const testKey = '__storage_test__';
    sessionStorage.setItem(testKey, 'test');
    sessionStorage.removeItem(testKey);
    return true;
  } catch (e) {
    console.warn('sessionStorage is not available, using memory fallback:', e);
    return false;
  }
}

const localStorageAvailable = isLocalStorageAvailable();
const sessionStorageAvailable = isSessionStorageAvailable();

/**
 * Safe storage wrapper that falls back to memory storage
 */
export const safeStorage = {
  /**
   * Get item from storage
   */
  getItem(key: string, useSession: boolean = false): string | null {
    try {
      // Try requested storage first
      if (useSession && sessionStorageAvailable) {
        return sessionStorage.getItem(key);
      }
      if (!useSession && localStorageAvailable) {
        return localStorage.getItem(key);
      }
      
      // Fallback: try the other storage type
      if (useSession && localStorageAvailable) {
        return localStorage.getItem(key);
      }
      if (!useSession && sessionStorageAvailable) {
        return sessionStorage.getItem(key);
      }
      
      // Final fallback: memory
      return memoryStorage[key] || null;
    } catch (e) {
      console.error('Error getting item from storage:', e);
      return memoryStorage[key] || null;
    }
  },

  /**
   * Set item in storage
   */
  setItem(key: string, value: string, useSession: boolean = false): void {
    try {
      if (useSession && sessionStorageAvailable) {
        sessionStorage.setItem(key, value);
      } else if (localStorageAvailable) {
        localStorage.setItem(key, value);
      }
      // Always set in memory as backup
      memoryStorage[key] = value;
    } catch (e) {
      console.error('Error setting item in storage:', e);
      // Fallback to memory only
      memoryStorage[key] = value;
    }
  },

  /**
   * Remove item from storage
   */
  removeItem(key: string, useSession: boolean = false): void {
    try {
      if (useSession && sessionStorageAvailable) {
        sessionStorage.removeItem(key);
      }
      if (localStorageAvailable) {
        localStorage.removeItem(key);
      }
      delete memoryStorage[key];
    } catch (e) {
      console.error('Error removing item from storage:', e);
      delete memoryStorage[key];
    }
  },

  /**
   * Clear all storage
   */
  clear(useSession: boolean = false): void {
    try {
      if (useSession && sessionStorageAvailable) {
        sessionStorage.clear();
      }
      if (localStorageAvailable) {
        localStorage.clear();
      }
      // Clear memory storage
      Object.keys(memoryStorage).forEach(key => delete memoryStorage[key]);
    } catch (e) {
      console.error('Error clearing storage:', e);
      Object.keys(memoryStorage).forEach(key => delete memoryStorage[key]);
    }
  },

  /**
   * Check if storage is available
   */
  isAvailable(useSession: boolean = false): boolean {
    return useSession ? sessionStorageAvailable : localStorageAvailable;
  },

  /**
   * Get storage type being used
   */
  getStorageType(): 'localStorage' | 'sessionStorage' | 'memory' {
    if (localStorageAvailable) return 'localStorage';
    if (sessionStorageAvailable) return 'sessionStorage';
    return 'memory';
  }
};

/**
 * Show warning to user if storage is not available
 */
export function checkStorageAndWarn(): void {
  if (!localStorageAvailable && !sessionStorageAvailable) {
    console.warn(
      '⚠️ Browser storage is disabled. This may happen in:\n' +
      '- Safari Private Browsing\n' +
      '- iOS with "Prevent Cross-Site Tracking" enabled\n' +
      '- Browsers with strict privacy settings\n\n' +
      'Your session will only persist while the tab is open.'
    );
  }
}
