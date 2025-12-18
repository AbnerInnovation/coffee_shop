import { ref, computed } from 'vue';
import { isElectron } from '@/utils/printHelpers';

export function useElectronPrint() {
  const isElectronApp = computed(() => isElectron());
  const printers = ref<any[]>([]);
  const isLoadingPrinters = ref(false);
  const selectedPrinter = ref<string | null>(null);

  const loadPrinters = async () => {
    if (!isElectronApp.value) {
      console.warn('⚠️ Not running in Electron, cannot load printers');
      return;
    }

    isLoadingPrinters.value = true;
    try {
      const electron = (window as any).electron;
      const availablePrinters = await electron.print.getPrinters();
      printers.value = availablePrinters;
      
      // Auto-select default printer
      const defaultPrinter = availablePrinters.find((p: any) => p.isDefault);
      if (defaultPrinter && !selectedPrinter.value) {
        selectedPrinter.value = defaultPrinter.name;
      }
      
    } catch (error) {
      console.error('❌ Error loading printers:', error);
    } finally {
      isLoadingPrinters.value = false;
    }
  };

  const printSilent = async (html: string, paperWidth: number = 80) => {
    if (!isElectronApp.value) {
      throw new Error('Silent printing only available in Electron');
    }

    try {
      const electron = (window as any).electron;
      const result = await electron.print.printSilent(
        html,
        selectedPrinter.value || undefined,
        paperWidth
      );

      if (!result.success) {
        throw new Error(result.error || 'Print failed');
      }

      return result;
    } catch (error) {
      throw error;
    }
  };

  const printWithDialog = async (html: string) => {
    if (!isElectronApp.value) {
      throw new Error('Electron printing only available in Electron app');
    }

    try {
      const electron = (window as any).electron;
      const result = await electron.print.printHTML(html);

      if (!result.success) {
        throw new Error(result.error || 'Print failed');
      }

      return result;
    } catch (error) {

      throw error;
    }
  };

  return {
    isElectronApp,
    printers,
    isLoadingPrinters,
    selectedPrinter,
    loadPrinters,
    printSilent,
    printWithDialog,
  };
}
