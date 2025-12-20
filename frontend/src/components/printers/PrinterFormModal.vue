<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex min-h-screen items-center justify-center p-4">
      <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
      
      <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ printer ? t('app.views.printers.edit_printer') : t('app.views.printers.add_printer') }}
          </h2>
        </div>

        <!-- Form Content -->
        <form @submit.prevent="handleSubmit" class="px-6 py-6">
          <div class="space-y-6">
            <!-- Basic Information Section -->
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 space-y-4">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Información Básica</h3>
              
              <!-- Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.views.printers.form.name') }}
                </label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  placeholder="Ej: Impresora Cocina Principal"
                  class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white px-4 py-2.5"
                />
              </div>

              <!-- Printer Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.views.printers.form.type') }}
                </label>
                <select
                  v-model="form.printer_type"
                  required
                  class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white px-4 py-2.5"
                >
                  <option value="kitchen">{{ t('app.views.printers.types.kitchen') }}</option>
                  <option value="bar">{{ t('app.views.printers.types.bar') }}</option>
                  <option value="cashier">{{ t('app.views.printers.types.cashier') }}</option>
                </select>
              </div>
            </div>

            <!-- Connection Settings Section -->
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 space-y-4">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Configuración de Conexión</h3>
              
              <!-- Connection Type -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.views.printers.form.connection_type') }}
                </label>
                <select
                  v-model="form.connection_type"
                  class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white px-4 py-2.5"
                >
                  <option value="network">Network (IP)</option>
                  <option value="usb">USB</option>
                  <option value="bluetooth">Bluetooth</option>
                </select>
              </div>

              <!-- Network Settings -->
              <div v-if="form.connection_type === 'network'" class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {{ t('app.views.printers.form.ip_address') }}
                  </label>
                  <input
                    v-model="form.ip_address"
                    type="text"
                    :required="form.connection_type === 'network'"
                    placeholder="192.168.1.100"
                    class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white px-4 py-2.5"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {{ t('app.views.printers.form.port') }}
                  </label>
                  <input
                    v-model.number="form.port"
                    type="number"
                    placeholder="9100"
                    class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white px-4 py-2.5"
                  />
                </div>
              </div>

              <!-- USB/Bluetooth Settings -->
              <div v-if="form.connection_type === 'usb' || form.connection_type === 'bluetooth'">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.views.printers.form.device_path') }}
                </label>
                <input
                  v-model="form.device_path"
                  type="text"
                  :placeholder="form.connection_type === 'usb' ? 'Windows: USB001, COM3 | Linux: /dev/usb/lp0' : 'Nombre del dispositivo Bluetooth'"
                  class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white px-4 py-2.5"
                />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {{ form.connection_type === 'usb' ? 'Ej: USB001 (Windows), /dev/usb/lp0 (Linux)' : 'Nombre del dispositivo emparejado' }}
                </p>
              </div>
            </div>

            <!-- Printer Settings Section -->
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 space-y-4">
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Configuración de Impresión</h3>
              
              <!-- Paper Width -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.views.printers.form.paper_width') }}
                </label>
                <div class="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    @click="form.paper_width = 58"
                    :class="[
                      'px-4 py-3 rounded-lg border-2 transition-all',
                      form.paper_width === 58
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                    ]"
                  >
                    <div class="text-lg font-bold">58mm</div>
                    <div class="text-xs text-gray-500">Compacto</div>
                  </button>
                  <button
                    type="button"
                    @click="form.paper_width = 80"
                    :class="[
                      'px-4 py-3 rounded-lg border-2 transition-all',
                      form.paper_width === 80
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300'
                        : 'border-gray-300 dark:border-gray-600 hover:border-gray-400'
                    ]"
                  >
                    <div class="text-lg font-bold">80mm</div>
                    <div class="text-xs text-gray-500">Estándar</div>
                  </button>
                </div>
              </div>

              <!-- Options Checkboxes -->
              <div class="space-y-3 pt-2">
                <label class="flex items-center p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4">
                  <span class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.printers.form.is_active') }}</span>
                </label>
                
                <label class="flex items-center p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  <input v-model="form.is_default" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4">
                  <span class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.printers.form.is_default') }}</span>
                </label>
                
                <label class="flex items-center p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer">
                  <input v-model="form.auto_print" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4">
                  <span class="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t('app.views.printers.form.auto_print') }}</span>
                </label>
              </div>
            </div>
          </div>
        </form>

        <!-- Footer Actions -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600 transition-colors"
          >
            {{ t('app.actions.cancel') }}
          </button>
          <button
            type="submit"
            @click="handleSubmit"
            class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
          >
            {{ t('app.actions.save') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Printer, PrinterCreate, PrinterUpdate } from '@/services/printerService';
import { PrinterType, ConnectionType } from '@/services/printerService';

const { t } = useI18n();

const props = defineProps<{
  printer?: Printer | null;
  categories: any[];
}>();

const emit = defineEmits<{
  close: [];
  save: [data: PrinterCreate | PrinterUpdate];
}>();

const form = ref<PrinterCreate>({
  name: '',
  printer_type: PrinterType.KITCHEN,
  connection_type: ConnectionType.NETWORK,
  ip_address: '',
  port: 9100,
  paper_width: 80,
  is_active: true,
  is_default: false,
  auto_print: true,
  print_copies: 1,
  category_ids: []
});

watch(() => props.printer, (printer) => {
  if (printer) {
    form.value = {
      name: printer.name,
      printer_type: printer.printer_type,
      connection_type: printer.connection_type,
      ip_address: printer.ip_address || '',
      port: printer.port || 9100,
      paper_width: printer.paper_width,
      is_active: printer.is_active,
      is_default: printer.is_default,
      auto_print: printer.auto_print,
      print_copies: printer.print_copies,
      category_ids: printer.category_ids
    };
  }
}, { immediate: true });

const handleSubmit = () => {
  emit('save', form.value);
};
</script>
