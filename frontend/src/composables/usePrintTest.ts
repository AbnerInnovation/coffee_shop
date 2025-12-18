import { ref, computed } from 'vue';
import { useKitchenPrint } from '@/composables/useKitchenPrint';
import { useCustomerPrint } from '@/composables/useCustomerPrint';
import { isElectron } from '@/utils/printHelpers';
import { useToast } from 'vue-toastification';
import mockOrderData from '@/mocks/mockOrder.json';

export function usePrintTest() {
  const toast = useToast();
  const kitchenPrint = useKitchenPrint();
  const customerPrint = useCustomerPrint();

  const logs = ref<string[]>([]);
  const mockOrder = mockOrderData;
  const isPrintingKitchen = ref(false);
  const isPrintingCustomer = ref(false);
  const isPrintingPreBill = ref(false);

  const isElectronApp = computed(() => isElectron());
  const isPrinting = computed(() => isPrintingKitchen.value || isPrintingCustomer.value || isPrintingPreBill.value);
  const printers = computed(() => kitchenPrint.electronPrint.printers.value);
  const isLoadingPrinters = computed(() => kitchenPrint.electronPrint.isLoadingPrinters.value);
  
  const selectedPrinter = computed({
    get: () => kitchenPrint.electronPrint.selectedPrinter.value,
    set: (val) => {
      kitchenPrint.electronPrint.selectedPrinter.value = val;
      customerPrint.electronPrint.selectedPrinter.value = val;
    }
  });

  const selectedPrinterInfo = computed(() => {
    if (!selectedPrinter.value) return null;
    return printers.value.find(p => p.name === selectedPrinter.value);
  });

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    logs.value.push(`[${timestamp}] ${message}`);
    setTimeout(() => {
      const container = document.querySelector('.overflow-y-auto');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 10);
  };

  const getPrinterStatus = (status: number): string => {
    const statuses: Record<number, string> = {
      0: 'Disponible',
      1: 'Imprimiendo',
      2: 'Error',
      3: 'Sin conexión'
    };
    return statuses[status] || 'Desconocido';
  };

  const loadPrinters = async () => {
    addLog('🔍 Buscando impresoras...');
    try {
      await kitchenPrint.electronPrint.loadPrinters();
      addLog(`✅ ${printers.value.length} impresoras encontradas`);
      printers.value.forEach(p => {
        addLog(`   - ${p.displayName || p.name}${p.isDefault ? ' (Predeterminada)' : ''}`);
      });
    } catch (error: any) {
      addLog(`❌ Error: ${error.message}`);
      toast.error('Error al cargar impresoras');
    }
  };

  const testKitchenPrint = async () => {
    if (isPrintingKitchen.value) return;
    
    isPrintingKitchen.value = true;
    addLog('🖨️ Imprimiendo ticket de cocina...');
    try {
      await kitchenPrint.printKitchenTicket(mockOrder);
      addLog('✅ Ticket de cocina impreso correctamente');
    } catch (error: any) {
      addLog(`❌ Error: ${error.message}`);
      toast.error('Error al imprimir ticket de cocina');
    } finally {
      isPrintingKitchen.value = false;
    }
  };

  const testCustomerReceipt = async () => {
    if (isPrintingCustomer.value) return;
    
    isPrintingCustomer.value = true;
    addLog('🖨️ Imprimiendo ticket de cliente...');
    try {
      await customerPrint.printCustomerReceipt(mockOrder);
      addLog('✅ Ticket de cliente impreso correctamente');
    } catch (error: any) {
      addLog(`❌ Error: ${error.message}`);
      toast.error('Error al imprimir ticket de cliente');
    } finally {
      isPrintingCustomer.value = false;
    }
  };

  const testPreBill = async () => {
    if (isPrintingPreBill.value) return;
    
    isPrintingPreBill.value = true;
    addLog('🖨️ Imprimiendo pre-cuenta...');
    try {
      await customerPrint.printPreBill(mockOrder);
      addLog('✅ Pre-cuenta impresa correctamente');
    } catch (error: any) {
      addLog(`❌ Error: ${error.message}`);
      toast.error('Error al imprimir pre-cuenta');
    } finally {
      isPrintingPreBill.value = false;
    }
  };

  const clearLogs = () => {
    logs.value = [];
  };

  return {
    // State
    logs,
    isElectronApp,
    isPrinting,
    isPrintingKitchen,
    isPrintingCustomer,
    isPrintingPreBill,
    printers,
    selectedPrinter,
    selectedPrinterInfo,
    isLoadingPrinters,
    
    // Methods
    loadPrinters,
    testKitchenPrint,
    testCustomerReceipt,
    testPreBill,
    getPrinterStatus,
    clearLogs
  };
}
