/**
 * Platform detection utilities
 * Detects if app is running in Electron (Desktop) or Web (Cloud)
 */

/**
 * Check if running in Electron environment
 */
export const isElectron = (): boolean => {
  // Check if window.electron exists (exposed via preload.ts)
  if (typeof window !== 'undefined' && (window as any).electron) {
    return true;
  }
  
  // Fallback: Check user agent
  if (typeof navigator !== 'undefined') {
    return navigator.userAgent.toLowerCase().includes('electron');
  }
  
  return false;
};

/**
 * Check if running in web/cloud environment
 */
export const isWeb = (): boolean => {
  return !isElectron();
};

/**
 * Get platform type
 */
export const getPlatform = (): 'electron' | 'web' => {
  return isElectron() ? 'electron' : 'web';
};

/**
 * Platform-specific feature flags
 */
export const platformFeatures = {
  /**
   * Features available only in Cloud (Web)
   */
  cloudOnly: {
    reports: isWeb(),
    users: isWeb(),
    subscription: isWeb(),
    analytics: isWeb(),
    auditLogs: isWeb(),
    sysadmin: isWeb(),
    menuManagement: isWeb(),
    categoryManagement: isWeb(),
  },
  
  /**
   * Features available in both platforms
   */
  shared: {
    orders: true,
    menuView: true,
    categoriesView: true,
    tables: true,
    cashRegister: true,
    kitchen: true,
    pos: true,
    profile: true,
  },
  
  /**
   * Features available only in Desktop (Electron)
   */
  desktopOnly: {
    offlineMode: isElectron(),
    bluetoothPrinting: isElectron(),
    localDatabase: isElectron(),
    multiplePrinters: isElectron(),
  }
};

/**
 * Check if a route should be available in current platform
 */
export const isRouteAvailable = (routeName: string): boolean => {
  const cloudOnlyRoutes = ['Reports', 'Users', 'Subscription', 'SysAdmin', 'PendingPayments', 'Configuration'];
  
  if (isElectron() && cloudOnlyRoutes.includes(routeName)) {
    return false;
  }
  
  return true;
};

/**
 * Get platform display name
 */
export const getPlatformName = (): string => {
  return isElectron() ? 'Desktop' : 'Cloud';
};
