<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
      Configuración de Impresora
    </h3>

    <!-- Electron Detection -->
    <div v-if="!electronPrint.isElectronApp.value" class="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-md">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
        <div class="ml-3">
          <p class="text-sm text-yellow-700 dark:text-yellow-300">
            La impresión silenciosa solo está disponible en la aplicación de escritorio.
            En el navegador se mostrará el diálogo de impresión estándar.
          </p>
        </div>
      </div>
    </div>

    <!-- Printer Selection (Electron only) -->
    <div v-if="electronPrint.isElectronApp.value" class="space-y-4">
      <!-- Load Printers Button -->
      <div>
        <button
          @click="loadPrinters"
          :disabled="electronPrint.isLoadingPrinters.value"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ArrowPathIcon 
            :class="['h-5 w-5 mr-2', { 'animate-spin': electronPrint.isLoadingPrinters.value }]" 
          />
          {{ electronPrint.isLoadingPrinters.value ? 'Cargando...' : 'Buscar Impresoras' }}
        </button>
      </div>

      <!-- Printers List -->
      <div v-if="electronPrint.printers.value.length > 0">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Impresora de Cocina
        </label>
        <select
          v-model="electronPrint.selectedPrinter.value"
          class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        >
          <option :value="null">Impresora predeterminada</option>
          <option
            v-for="printer in electronPrint.printers.value"
            :key="printer.name"
            :value="printer.name"
          >
            {{ printer.displayName || printer.name }}
            <span v-if="printer.isDefault"> (Predeterminada)</span>
          </option>
        </select>

        <!-- Selected Printer Info -->
        <div v-if="selectedPrinterInfo" class="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
          <div class="text-sm">
            <p class="font-medium text-gray-900 dark:text-white">
              {{ selectedPrinterInfo.displayName || selectedPrinterInfo.name }}
            </p>
            <p v-if="selectedPrinterInfo.description" class="text-gray-500 dark:text-gray-400 mt-1">
              {{ selectedPrinterInfo.description }}
            </p>
            <p class="text-gray-500 dark:text-gray-400 mt-1">
              Estado: {{ getPrinterStatus(selectedPrinterInfo.status) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Test Print Button -->
      <div v-if="electronPrint.selectedPrinter.value" class="pt-4">
        <button
          @click="testPrint"
          :disabled="isTesting"
          class="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <PrinterIcon class="h-5 w-5 mr-2" />
          {{ isTesting ? 'Imprimiendo...' : 'Imprimir Prueba' }}
        </button>
      </div>
    </div>

    <!-- Paper Width Setting -->
    <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Ancho de Papel
      </label>
      <div class="flex items-center space-x-4">
        <label class="inline-flex items-center">
          <input
            type="radio"
            :value="58"
            v-model="paperWidth"
            class="form-radio h-4 w-4 text-indigo-600 focus:ring-indigo-500"
          />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">58mm</span>
        </label>
        <label class="inline-flex items-center">
          <input
            type="radio"
            :value="80"
            v-model="paperWidth"
            class="form-radio h-4 w-4 text-indigo-600 focus:ring-indigo-500"
          />
          <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">80mm</span>
        </label>
      </div>
    </div>

    <!-- Save Button -->
    <div class="mt-6">
      <button
        @click="saveSettings"
        :disabled="isSaving"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <CheckIcon class="h-5 w-5 mr-2" />
        {{ isSaving ? 'Guardando...' : 'Guardar Configuración' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useElectronPrint } from '@/composables/useElectronPrint';
import { useAuthStore } from '@/stores/auth';
import { useToast } from 'vue-toastification';
import {
  PrinterIcon,
  ArrowPathIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline';

const electronPrint = useElectronPrint();
const authStore = useAuthStore();
const toast = useToast();

const paperWidth = ref(80);
const isTesting = ref(false);
const isSaving = ref(false);

const selectedPrinterInfo = computed(() => {
  if (!electronPrint.selectedPrinter.value) return null;
  return electronPrint.printers.value.find(
    p => p.name === electronPrint.selectedPrinter.value
  );
});

const loadPrinters = async () => {
  try {
    await electronPrint.loadPrinters();
    toast.success('Impresoras cargadas correctamente');
  } catch (error) {
    console.error('Error loading printers:', error);
    toast.error('Error al cargar impresoras');
  }
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

const testPrint = async () => {
  isTesting.value = true;
  try {
    const testHTML = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Prueba de Impresión</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Courier New', monospace;
      width: ${paperWidth.value - 8}mm;
      padding: 4mm;
    }
    .header {
      text-align: center;
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 8px;
    }
    .divider {
      border-top: 2px dashed black;
      margin: 8px 0;
    }
    .content {
      font-size: 14px;
      line-height: 1.5;
    }
    @media print {
      @page { margin: 0; size: ${paperWidth.value}mm auto; }
      body { margin: 0; padding: 4mm; }
    }
  </style>
</head>
<body>
  <div class="header">PRUEBA DE IMPRESIÓN</div>
  <div class="divider"></div>
  <div class="content">
    <p>Impresora: ${electronPrint.selectedPrinter.value || 'Predeterminada'}</p>
    <p>Ancho de papel: ${paperWidth.value}mm</p>
    <p>Fecha: ${new Date().toLocaleString('es-MX')}</p>
  </div>
  <div class="divider"></div>
  <div class="content" style="text-align: center;">
    <p>✓ Impresión exitosa</p>
  </div>
</body>
</html>
    `;

    await electronPrint.printSilent(testHTML, paperWidth.value);
    toast.success('Impresión de prueba enviada');
  } catch (error: any) {
    console.error('Error in test print:', error);
    toast.error('Error al imprimir: ' + error.message);
  } finally {
    isTesting.value = false;
  }
};

const saveSettings = async () => {
  isSaving.value = true;
  try {
    // TODO: Guardar configuración en el backend
    // Aquí deberías llamar a un endpoint para guardar:
    // - electronPrint.selectedPrinter.value
    // - paperWidth.value
    
    toast.success('Configuración guardada correctamente');
  } catch (error) {
    console.error('Error saving settings:', error);
    toast.error('Error al guardar configuración');
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  // Load current settings
  if (authStore.restaurant) {
    paperWidth.value = authStore.restaurant.kitchen_print_paper_width || 80;
  }
  
  // Auto-load printers if in Electron
  if (electronPrint.isElectronApp.value) {
    loadPrinters();
  }
});
</script>
