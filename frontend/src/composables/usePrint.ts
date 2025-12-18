import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { openPrintWindow, isElectron } from '@/utils/printHelpers';
import { useElectronPrint } from './useElectronPrint';

/**
 * Configuration for a print job
 */
export interface PrintConfig {
  paperWidth?: number;
  printerName?: string;
  enabledSettingKey?: string; // Key in restaurant settings to check if printing is enabled
  paperWidthKey?: string;     // Key in restaurant settings for paper width
  printerNameKey?: string;     // Key in restaurant settings for printer name
}

/**
 * Generic composable for printing with Electron support
 * Handles both silent printing (Electron) and browser print dialog
 * Eliminates code duplication across different print types
 */
export function usePrint() {
  const authStore = useAuthStore();
  const isPrinting = ref(false);
  const electronPrint = useElectronPrint();

  /**
   * Check if printing is enabled based on restaurant settings
   */
  const isPrintEnabled = (settingKey?: string, defaultValue = true): boolean => {
    if (!settingKey) return defaultValue;
    return (authStore.restaurant as any)?.[settingKey] ?? defaultValue;
  };

  /**
   * Get print configuration from restaurant settings
   */
  const getPrintConfig = (config: PrintConfig): Required<Omit<PrintConfig, 'enabledSettingKey' | 'paperWidthKey' | 'printerNameKey'>> => {
    const paperWidth = config.paperWidth || 
      (config.paperWidthKey ? (authStore.restaurant as any)?.[config.paperWidthKey] : null) || 
      80;
    
    const printerName = config.printerName || 
      (config.printerNameKey ? (authStore.restaurant as any)?.[config.printerNameKey] : null) || 
      null;

    return { paperWidth, printerName };
  };

  /**
   * Generic print function that works with any HTML
   * Automatically detects Electron and uses silent printing or browser dialog
   * 
   * @param html - The HTML content to print
   * @param config - Print configuration (paper width, printer name, settings keys)
   * @param logPrefix - Prefix for console logs (e.g., 'Kitchen', 'Customer', 'Report')
   * @returns Promise that resolves when printing is complete
   */
  const print = async (
    html: string,
    config: PrintConfig = {},
    logPrefix = 'Document'
  ): Promise<void> => {
    // Check if printing is enabled
    if (config.enabledSettingKey && !isPrintEnabled(config.enabledSettingKey)) {
      return;
    }

    isPrinting.value = true;

    try {
      // Ensure restaurant data is loaded
      if (!authStore.restaurant) {
        await authStore.loadRestaurant();
      }

      // Get print configuration
      const { paperWidth, printerName } = getPrintConfig(config);

      // Use Electron silent print if available, otherwise browser print
      if (isElectron() && electronPrint.isElectronApp.value) {
        
        // Set printer if configured
        if (printerName) {
          electronPrint.selectedPrinter.value = printerName;
        }
        
        // Print silently (no dialog)
        await electronPrint.printSilent(html, paperWidth);
      } else {
        // Open print window and trigger print dialog
        await openPrintWindow(html);
      }
    } catch (error) {
      console.error(`❌ Error printing ${logPrefix.toLowerCase()}:`, error);
      throw error;
    } finally {
      isPrinting.value = false;
    }
  };

  /**
   * Print with a custom HTML builder function
   * Useful when you need to generate HTML based on data
   * 
   * @param data - Data to pass to the HTML builder
   * @param htmlBuilder - Function that generates HTML from data and paper width
   * @param config - Print configuration
   * @param logPrefix - Prefix for console logs
   */
  const printWithBuilder = async <T>(
    data: T,
    htmlBuilder: (data: T, paperWidth: number) => string,
    config: PrintConfig = {},
    logPrefix = 'Document'
  ): Promise<void> => {
    // Get paper width first
    const { paperWidth } = getPrintConfig(config);
    
    // Build HTML
    const html = htmlBuilder(data, paperWidth);
    
    // Print
    await print(html, config, logPrefix);
  };

  return {
    isPrinting,
    isPrintEnabled,
    getPrintConfig,
    print,
    printWithBuilder,
    electronPrint
  };
}
